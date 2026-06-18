# sources/control-plane/mayastor/io-engine/tests/nvme_device_timeout.rs

Purpose: verifies NVMe bdev timeout actions: `Reset` completes a hung read with an error callback, while `Ignore` leaves the operation outstanding until device destruction.

Important APIs/types/functions: `Config`, `NvmeBdevOpts`, `DeviceTimeoutAction`, `BlockDevice`, `BlockDeviceHandle`, `IoCompletionStatus`, `ReadOptions`, `DmaBuf`, `AsIoVecs`, `AtomicPtr`, `AtomicCell`, `OnceCell`, `device_create`, `device_open`, `device_destroy`, and `test_io_timeout`.

Control flow: tests configure short NVMe timeouts, create and share a remote malloc bdev, import it locally, open an I/O handle, set the timeout action, pause the target container, submit `readv_blocks` with a raw context pointer, and observe callback behavior. `io_timeout_reset` expects one non-success callback. `io_timeout_ignore` waits several timeout intervals and asserts the callback flag remains false before destroying the device.

State and persistence behavior: no persistent store. State is local imported device lifetime, timeout policy, outstanding I/O, DMA buffer lifetime, and callback flag.

Dependencies and integration points: compose pause, NVMf bdev share, local SPDK bdev import, NVMe transport config, DMA buffers, and C-style callbacks.

Risks: unsafe raw-pointer ownership depends on cleanup executing; timing depends on SPDK/kernel timeout behavior and container pause semantics.

Test signals: timeout action round-trips, callback receives correct device/context, reset mode errors, ignore mode does not callback, and destroy succeeds.
