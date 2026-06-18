<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c

## Purpose
SDK7786 NMI mode parser and initializer. It parses an nmi_mode setup option, programs FPGA NMI routing/mode bits, and reports invalid mode strings.

## Important APIs, Types, and Functions
- functions: nmi_mode_setup, sdk7786_nmi_init.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/kernel.h, linux/string.h, mach/fpga.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/nmi.c -->
