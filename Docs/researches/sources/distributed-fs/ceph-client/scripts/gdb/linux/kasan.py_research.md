# sources/distributed-fs/ceph-client/scripts/gdb/linux/kasan.py

## Purpose
`kasan.py` registers `lx-kasan_mem_to_shadow`, which translates a kernel memory address to its KASAN shadow address for generic or software-tagged KASAN configurations.

## Important APIs, Types, and Functions
`KasanMemToShadow` lazily initializes `mm.page_ops().ops` and uses `KASAN_SHADOW_SCALE_SHIFT` plus `KASAN_SHADOW_OFFSET` to compute `(addr >> scale) + offset`.

## Control Flow
The command is registered only when KASAN generic or SW tags are configured. `invoke()` validates one hex argument, initializes page operations on first use, computes the shadow address, and prints it.

## State and Persistence Behavior
The command is read-only. It keeps one cached `p_ops` object across invocations, so changes to loaded objfiles or architecture context are not automatically reflected inside this command instance.

## Dependencies and Integration Points
It depends on KASAN constants exposed through `linux.constants` and architecture memory constants assembled in `linux.mm`.

## Risks and Test Signals
The guard condition in `invoke()` mixes `not CONFIG_KASAN_GENERIC` with `or CONFIG_KASAN_SW_TAGS`, which can reject SW-tagged configurations despite registration intent. Validate with known KASAN shadow mappings on arm64 and generic KASAN kernels.
