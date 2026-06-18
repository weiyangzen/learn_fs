# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_desc_regs.h

## Purpose
`rot0_desc_regs.h` defines the descriptor-register address map for Gaudi2 rotator instance 0. These registers describe an image rotation/warp job, completion message behavior, AXI attributes, and descriptor push.

## Important APIs, Types, And Functions
The exported macros cover context ID, input/output image base addresses, transform configuration, sine/cosine and affine matrix coefficients, input/output image geometry, strides, stripes, centers, background/padding, completion message address/data/AWUSER, idle state, read/write AXUSER fields, output window and buffer control, mesh image configuration, precision and clamping controls, and `PUSH_DESC`.

## Control Flow
There is no C control flow. Hardware flow is descriptor-driven: the driver writes a complete descriptor register set, configures completion messaging, then writes `PUSH_DESC` to submit work to the rotator. Status/idle registers indicate whether the descriptor path is ready or finished.

## State, Persistence, And Dependencies
Descriptor state is held by hardware registers until overwritten, consumed, or reset. Address fields are split low/high, so callers must program coherent 64-bit device addresses and AXUSER attributes. The header depends on matching rotator global registers and masks for status, error, and halt handling.

## Integration Points
The descriptor block integrates with queue-manager command submission, completion queues, memory-management/AXUSER programming, and rotator error handling. Security code also treats the rotator register ranges as protected MMIO windows.

## Risks
Partial descriptor programming can submit malformed jobs. Geometry, stride, mesh, and coefficient registers are tightly coupled; inconsistent values can cause out-of-bounds reads/writes or wrong image output. Completion message address/AWUSER mistakes can corrupt host-visible queues or fail to notify the driver.

## Test Signals
Useful tests include known-angle rotation outputs, mesh-mode transforms, completion interrupt/message delivery, idle-state polling, invalid descriptor rejection, address high/low programming, and reset recovery after a halted rotator.
