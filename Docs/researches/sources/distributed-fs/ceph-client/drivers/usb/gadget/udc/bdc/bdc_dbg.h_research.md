<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h

## Purpose
This header declares BDC verbose debug helpers and supplies no-op inline replacements when verbose gadget debugging is not built.

## Important APIs, Types, And Functions
With `CONFIG_USB_GADGET_VERBOSE`, it declares `bdc_dbg_bd_list()`, `bdc_dbg_srr()`, `bdc_dbg_regs()`, and `bdc_dump_epsts()`. Otherwise each helper is an empty static inline function.

## Control Flow
The header lets production code call debug helpers without wrapping every call site in preprocessor conditionals. The build either links `bdc_dbg.o` or compiles calls away.

## State And Persistence
No state is stored in this header. Debug implementations only observe controller, endpoint, and ring state.

## Dependencies And Integration Points
It includes `bdc.h` for `struct bdc` and `struct bdc_ep`. It is used by core, command, and endpoint implementation files.

## Risks
Because no-op functions erase calls entirely, debug-only timing or read side effects must not be required for correctness. The header comment describes debug functions correctly here, unlike the command header.

## Test Signals
Compile both with and without `CONFIG_USB_GADGET_VERBOSE`; endpoint/core code should require no additional `#ifdef`s.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_dbg.h -->
