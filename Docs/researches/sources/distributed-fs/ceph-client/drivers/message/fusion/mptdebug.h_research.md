# sources/distributed-fs/ceph-client/drivers/message/fusion/mptdebug.h

## Purpose
`mptdebug.h` centralizes Fusion MPT debug category bits, conditional print macros, and optional verbose frame dump helpers. It lets each protocol driver compile debug logging behind `CONFIG_FUSION_LOGGING` and gate runtime output through `ioc->debug_level`.

## Important APIs, Types, and Functions
Debug bits include `MPT_DEBUG`, `MPT_DEBUG_MSG_FRAME`, `MPT_DEBUG_SG`, `MPT_DEBUG_EVENTS`, `MPT_DEBUG_VERBOSE_EVENTS`, `MPT_DEBUG_INIT`, `MPT_DEBUG_EXIT`, `MPT_DEBUG_FAIL`, `MPT_DEBUG_TM`, `MPT_DEBUG_DV`, `MPT_DEBUG_REPLY`, `MPT_DEBUG_HANDSHAKE`, `MPT_DEBUG_CONFIG`, `MPT_DEBUG_DL`, `MPT_DEBUG_RESET`, `MPT_DEBUG_SCSI`, `MPT_DEBUG_IOCTL`, `MPT_DEBUG_FC`, `MPT_DEBUG_SAS`, `MPT_DEBUG_SAS_WIDE`, and `MPT_DEBUG_36GB_MEM`. Category macros include `dprintk`, `dsgprintk`, `devtprintk`, `dtmprintk`, `dctlprintk`, `dfcprintk`, and similar wrappers. Verbose helpers dump firmware download, request, reply, and task-management frames when `MPT_DEBUG_VERBOSE` and logging are enabled.

## Control Flow
Callers wrap `printk()` calls in a category macro. With logging enabled, `MPT_CHECK_LOGGING()` checks `IOC->debug_level & BITS` before executing the command. Without logging, the macro compiles to a no-op. Verbose dump functions additionally check message-frame or task-management bits before iterating over little-endian frame words.

## State and Persistence
The file stores no state. Runtime behavior depends on per-adapter `debug_level`, which can be set via module parameter or sysfs according to the header comments. Log output persists only through the kernel logging facility.

## Dependencies and Integration Points
It depends on `MPT_ADAPTER` being visible from `mptbase.h`, endian conversion helpers, and kernel `printk`. The macros are used throughout the Fusion base, SCSI, FC, SAS, LAN, and ioctl modules to avoid each file carrying its own logging gates.

## Risks and Edge Cases
Macros evaluate caller-provided command blocks, so arguments must be side-effect safe when logging is disabled. Verbose dump helpers assume valid frame pointers and sizes such as `ioc->req_sz`; using them on malformed frames can read unexpected words. Logging can be extremely noisy and may expose raw command or firmware data in kernel logs.

## Test Signals
Build tests should cover `CONFIG_FUSION_LOGGING` on and off, plus `MPT_DEBUG_VERBOSE` on and off. Runtime tests can set `debug_level` bits and confirm only matching categories emit logs while no-op builds produce no references to verbose helpers.
