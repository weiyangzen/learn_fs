<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c

## Purpose
`xe_exec.c` implements the user exec ioctl for GPU command submission. It is the high-level path that validates a user exec request, parses sync objects, locks and validates the VM, creates a scheduler job, wires dependencies and output fences, then submits to the exec queue backend.

## Important APIs, types, and functions
`xe_exec_fn()` injects VM validation/rebind into the `drm_gpuvm_exec` locking loop. `xe_exec_ioctl()` handles `DRM_XE_EXEC`: queue lookup, argument validation, sync parsing, batch address copy for parallel queues, hardware-engine-group mode selection, VM locking, userptr pin/recheck, validation, protected VM checks, job creation, dependency setup, user fence setup, last-fence update, job push, and cleanup.

## Control flow and integration points
The ioctl rejects extensions/padding/reserved fields, queue VM-bind misuse, mismatched batch count and queue width, reset queues, and too many queued jobs. For empty submissions, it only converts in-fences to out-fences and updates the last fence. For real execs it blocks on suspend, runs validation for non-LR VMs, checks closed/banned VM state, validates PXP, creates a job, adds VM rebind and sync dependencies, locks SVM notifier state for userptr repin checks, arms the job as the point of no return, installs dma-resv bookkeeping and sync outputs, pushes the job, and resumes faulting LR jobs when needed.

## State and persistence behavior
The path mutates queue job counts through job lifetime, VM validation state, dma-resv fence slots, syncobj/user-fence outputs, queue last-fence state, VM rebind activity, LRU bulk-move placement, and hardware-engine-group execution mode references.

## Dependencies, risks, and test signals
Dependencies include DRM exec/GPUVM, Xe VM/userptr/SVM, exec queues, hw engine groups, scheduler jobs, sync parsing, PM suspend blocking, PXP, and tracepoints. Risks include lock ordering around VM and dma-resv, repin retry loops, mode get/put imbalance, point-of-no-return error semantics, user fence limits, and LR/non-LR divergence. Test signals include exec ioctl validation, parallel submissions, empty exec/fence conversion, userptr invalidation races, VM ban/close, PXP protected queues, suspend freezer interruption, LR fault resume, syncobj/user-fence behavior, and max-job backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.c -->
