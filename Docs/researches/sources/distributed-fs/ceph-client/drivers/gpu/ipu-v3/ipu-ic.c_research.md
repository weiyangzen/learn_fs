# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic.c

## Purpose
Implements IPUv3 Image Converter task control for preprocessing, viewfinder, and post-processing tasks. It configures resizing, CSC, combiner, rotation, IDMAC task dimensions, and IC/IRT module enablement.

## Important APIs, Types, and Functions
`struct ic_task_regoffs` and `struct ic_task_bitfields` map task-specific register offsets and bit positions. `struct ipu_ic` represents an individual task, while `struct ipu_ic_priv` owns the MMIO base, task parameter memory, spinlock, task array, and use count. Exported APIs include `ipu_ic_task_enable()/disable()`, `ipu_ic_task_init_rsc()`, `ipu_ic_task_init()`, `ipu_ic_task_idma_init()`, `ipu_ic_enable()/disable()`, `ipu_ic_get()/put()`, `ipu_ic_init()/exit()`, and `ipu_ic_dump()`.

## Control Flow
Clients acquire an IC task, initialize resizing/CSC with `ipu_ic_task_init_rsc()` or `ipu_ic_task_init()`, initialize associated IDMAC channel parameters with `ipu_ic_task_idma_init()`, enable the IC module, then enable the task. The task init path validates resize limits, computes downsizing and resize coefficients, writes CSC coefficients into task parameter memory, and sets task bits. Disable clears task bits, rotation/IRT state, and module enable as appropriate.

## State and Persistence
Mutable state includes task `inuse` flags, IC module use count, and hardware registers/task parameter memory. A spinlock serializes most register and allocation operations. Hardware state persists until disabled, reset, or overwritten.

## Dependencies and Integration Points
Depends on `ipu-ic-csc.c` for CSC descriptors, CPMEM/IDMAC channel setup, common module enable/disable, and image-convert clients. The IRT rotation path uses common module bits for rotation-specific hardware.

## Risks
Resize coefficients have hardware limits; invalid dimensions return errors but borderline rounding can affect image quality. Multiple tasks share global IC registers and parameter memory, so locking and use count correctness are critical. Rotation paths require coordinated IDMAC links and IRT enablement; partial failures can leave modules enabled if caller unwinding is wrong.

## Test Signals
Coverage should include all IC tasks, resize up/down limits, CSC on/off, rotation and non-rotation IDMAC initialization, task allocation contention, and dump inspection. End-to-end image conversion CRCs are the best behavioral signal.
