<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gnss.h -->
# sources/distributed-fs/ceph-client/include/linux/gnss.h

Purpose: Defines the GNSS receiver character-device framework used by drivers that expose raw navigation data streams to userspace.

Important APIs/types/functions: `enum gnss_type` covers NMEA, SiRF, UBX, MTK, and count. `gnss_operations` provides open, close, and raw write callbacks. `gnss_device` embeds device/cdev IDs, type, flags, rw semaphore, ops, open count, disconnected flag, read mutex/FIFO/wait queue, write mutex, and write buffer. APIs include allocate/put/register/deregister, `gnss_insert_raw()`, and drvdata accessors.

Control flow: Drivers allocate and register a GNSS device. Userspace opens the cdev, causing driver open; driver receive paths push raw bytes with `gnss_insert_raw()` into a FIFO and wake readers; userspace writes are passed to `write_raw()` under write serialization; close tears down per-open state.

State and persistence behavior: Runtime state includes cdev/device registration, FIFO contents, open count, disconnected flag, and driver-private data. No persistent positioning state is stored here.

Dependencies and integration points: Depends on cdev/device core, kfifo, mutexes, rwsems, waits, and types. Integrates with serial/USB/platform GNSS receiver drivers.

Risks: FIFO overflow/backpressure behavior must be handled by implementation. Disconnect races are guarded by rwsem and flags; driver callbacks must respect lifecycle. Writes are raw protocol data and require device-specific validation.

Test signals: Register/open/read/write/close tests, disconnect during blocking read/write, FIFO overflow handling, multi-reader/writer serialization, and driver unregister cleanup under KASAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gnss.h -->
