# sources/distributed-fs/ceph-client/drivers/hv/mshv.h

## Purpose

`mshv.h` is the small shared public-internal header for Microsoft Hyper-V partition management helpers. It provides a reserved-field validation macro and declares common hypercall wrappers used by MSHV root, VTL, and related modules.

## Important APIs, Types, and Functions

- `mshv_field_nonzero(STRUCT, MEMBER)` uses `memchr_inv` and `sizeof_field` to detect non-zero reserved fields in copied user ABI structures.
- `hv_call_get_vp_registers()` and `hv_call_set_vp_registers()` batch Hyper-V VP register get/set operations for a target partition and VP.
- `hv_call_get_partition_property()` reads a scalar Hyper-V partition property.

## Control Flow

Consumers copy user or internal request structures, validate reserved fields with `mshv_field_nonzero`, then call the wrapper functions rather than directly formatting Hyper-V input pages. The concrete implementations in `mshv_common.c` serialize per-CPU hypercall input/output page usage by disabling local interrupts.

## State and Persistence Behavior

The header owns no persistent state. Its APIs operate on caller-supplied register arrays and output pointers. State lives in Hyper-V, the per-CPU hypercall pages, and higher-level partition/VP objects.

## Dependencies and Integration Points

It includes standard Linux string/field helpers and `hyperv/hvhdk.h`. The prototypes are consumed by `mshv_root_main.c`, `mshv_synic.c`, and VTL code paths that need partition properties or VP registers.

## Risks and Edge Cases

The reserved-field macro evaluates the passed structure expression for address computation and is intended for real objects, not side-effect expressions. Wrapper callers must provide arrays sized for `count`; batching is handled internally but not allocation. Property values are raw Hyper-V semantics and require caller-specific interpretation.

## Test Signals

Compile coverage should catch prototype drift against `mshv_common.c`. ABI tests should verify reserved fields reject non-zero bytes. Hypercall wrapper tests should cover multi-batch register get/set, failures converted with `hv_result_to_errno`, and property reads for valid and invalid property codes.
