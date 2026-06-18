# sources/distributed-fs/ceph-client/drivers/macintosh/via-cuda.c

Purpose: implements Cuda/Egret system controller transport over a 6522 VIA. These microcontrollers provide power/PRAM/RTC and ADB services on PowerMac and 68k Mac systems.

Important APIs and functions: `find_via_cuda()` locates/maps hardware and synchronizes the MCU. `via_cuda_driver` implements ADB callbacks through `cuda_probe()`, `cuda_send_request()`, `cuda_adb_autopoll()`, `cuda_reset_adb_bus()`, and `cuda_poll()`. `cuda_request()` is exported for CUDA packet users. `cuda_interrupt()` is the core state machine; `cuda_input()` dispatches unsolicited packets. RTC helpers are `cuda_get_time()` and `cuda_set_rtc_time()`.

Control flow: initialization maps VIA registers, configures the shift register, performs Cuda or Egret-specific sync, enables autopoll, then requests the IRQ at device init. Requests are queued under `cuda_lock`; `cuda_start()` begins output if no incoming byte is pending. The interrupt state machine handles collisions, byte sends, awaited replies, unsolicited reads, Egret quirks without final interrupts, queue advancement, and callback execution outside the lock.

State and persistence: global VIA pointer, queue pointers, `cuda_state`, reply buffer, current reply pointer, index flags, IRQ, OF node, and fully-inited flag. RTC persists in hardware; driver state does not.

Dependencies and integration: depends on PPC OF or m68k Macintosh config, VIA register layout, unified ADB, CUDA packet definitions, IRQ handling, XMON optional keyboard interception, and RTC conversion offset from 1904 to 1970.

Risks: protocol correctness is timing-sensitive and differs for Egret active levels/delays. Synchronous calls busy-poll. Reply buffers are bounded to 16 bytes with overflow discard. Request lifetime assumptions mirror ADB core expectations. Collision handling and lock break before `cuda_input()` are reentrancy-sensitive.

Test signals: Cuda and Egret detection, sync completion, ADB keyboard/mouse autopoll, CUDA request/reply, RTC get/set, unsolicited packet logging, IRQ and polling paths, collision recovery, and behavior on both PPC and m68k builds.
