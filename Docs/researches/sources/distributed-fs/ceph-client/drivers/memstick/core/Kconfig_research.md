# sources/distributed-fs/ceph-client/drivers/memstick/core/Kconfig

Purpose: This Kconfig file defines core MemoryStick policy and block-driver options under the top-level MemoryStick subsystem.

Important APIs/types/functions: `MEMSTICK_UNSAFE_RESUME` allows skipping normal removal/redetection across suspend, explicitly warning about data corruption risk. `MSPRO_BLOCK` enables the MemoryStick Pro block driver and depends on `BLOCK`. `MS_BLOCK` enables the older MemoryStick Standard block driver, also depending on `BLOCK`. Both block drivers imply `IOSCHED_BFQ`.

Control flow: These options are visible only when the parent `MEMSTICK` menu sources this file. Selected options drive object inclusion in `drivers/memstick/core/Makefile`.

State and persistence: Options persist in kernel configuration. Runtime behavior is affected by compiled-in code paths, especially unsafe resume policy in core/card handling.

Dependencies and integration: Integrates with block layer availability, BFQ scheduler hints, MemoryStick core bus code, and the two block driver source files compiled by the core Makefile.

Risks and test signals: The notable risk is `MEMSTICK_UNSAFE_RESUME`, which can corrupt data if cards are removed during suspend. Driver options also carry media compatibility risk: Standard and Pro cards require different drivers. Test signals include Kconfig dependency checks with `BLOCK=n`, building each driver as module/built-in, and suspend/resume tests with unsafe resume disabled and enabled only on fixed-media systems.
