# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Makefile

## Purpose

This Makefile maps Speed Select Kconfig symbols to module objects.

## Important APIs, Types, And Functions

`CONFIG_INTEL_SPEED_SELECT_INTERFACE` builds `isst_if_common.o`, `isst_if_mmio.o`, `isst_if_mbox_pci.o`, and `isst_if_mbox_msr.o`. `CONFIG_INTEL_SPEED_SELECT_TPMI` builds `isst_tpmi_core.o` and `isst_tpmi.o`.

## Control Flow

There is no runtime control flow; Kbuild uses these object lists to compile and link the selected modules.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The object ordering separates common char-device code, legacy backends, and TPMI backend glue/core.

## Risks

Because common and backend objects are independent modules, namespace exports and module load ordering matter. Missing common module prevents backend registration with `/dev/isst_interface`.

## Test Signals

Build with interface only and interface plus TPMI, inspect produced modules, and run modprobe dependency checks.
