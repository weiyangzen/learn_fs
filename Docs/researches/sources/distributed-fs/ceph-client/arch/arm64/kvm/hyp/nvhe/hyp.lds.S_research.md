<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S

## Purpose
`hyp.lds.S` is the partial-link linker script for nVHE EL2 objects. It groups and renames hyp sections so they can later be linked into vmlinux while retaining distinct hyp text, rodata, data, percpu, bss, idmap text, and optional tracing event-id ranges.

## Important APIs, Types, and Functions
The script uses `HYP_SECTION(...)`, `BEGIN_HYP_SECTION(...)`, and `END_HYP_SECTION` macros from `asm/hyp_image.h`. It emits `.idmap.text`, `.text`, `.data..ro_after_init`, `.rodata`, optional `.event_ids`, page-aligned `.data..percpu` using `PERCPU_INPUT(L1_CACHE_BYTES)`, `.bss`, and `.data`.

## Control Flow, State, and Persistence
There is no runtime control flow. Its persistent effect is the shape and alignment of the intermediate hyp ELF. Page-aligning percpu sections preserves alignment when embedded in vmlinux; optional tracing event ids are sorted and page-aligned for runtime lookup.

## Dependencies and Integration Points
It is consumed by the kernel build and paired with `gen-hyprel.c`, hyp image macros, vmlinux linker definitions, per-CPU data access in `hyp-smp.c`, and tracing event metadata in `trace.c` / hypevents.

## Risks and Test Signals
Risks include section-order changes breaking runtime symbol assumptions, missing alignment for percpu or tracing metadata, and mismatches with relocation generation. Test signals are successful nVHE partial linking, expected `__hyp_section_*` symbols, per-CPU alignment checks, optional tracing builds, and boot-time hyp relocation success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S -->
