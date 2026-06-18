<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/broadsheetfb.h -->
# sources/distributed-fs/ceph-client/include/video/broadsheetfb.h

Purpose: defines Broadsheet e-paper framebuffer command/register constants and the board abstraction used by the broadsheet framebuffer driver.

Important APIs and types: command macros cover system/display init, register read/write, image load/load-area/end, wait triggers, waveform info, and full/update commands. Interface constants distinguish control pins and MMIO command/data writes. `broadsheetfb_par` holds fb info, board callbacks, register accessors, waitqueue, panel index, and IO lock. `broadsheet_board` supplies init/wait/cleanup/panel/IRQ plus GPIO or MMIO access callbacks.

Control flow: the driver initializes board hardware, writes controller registers/commands, loads image data, waits for display triggers/frame-end, and performs e-paper update sequences through board-specific GPIO/MMIO operations.

State and persistence: runtime state includes panel index, waitqueue events, IO lock, controller registers, and board-specific GPIO/MMIO state. Display contents may persist physically on e-paper but are not kernel-persistent data.

Dependencies and integration points: depends on fbdev, wait queues, mutexes, modules, and board glue. It integrates with platform-specific Broadsheet boards and framebuffer update paths.

Risks and test signals: risks include board callback lifetime, IO locking, wait-for-ready timeouts, panel type mismatch, and command ordering for e-paper updates. Test init/update/cleanup, IRQ wait paths, GPIO and MMIO boards, partial/full image loads, and timeout/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/broadsheetfb.h -->
