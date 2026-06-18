# sources/distributed-fs/ceph-client/scripts/gen-btf.sh

## Purpose
`gen-btf.sh` generates BTF data for a target ELF, handling the different final embedding/linking flows for vmlinux and modules.

## Important APIs, Types, and Functions
Shell functions include `usage()`, `is_enabled()`, `gen_btf_data()`, `gen_btf_o()`, `embed_btf_data()`, and `cleanup()`. Inputs are environment tools/flags such as `PAHOLE`, `RESOLVE_BTFIDS`, `OBJCOPY`, `CC`, `KBUILD_*`, `CLANG_FLAGS`, `objtree`, and optional `--btf_base`.

## Control Flow
Argument parsing sets `BTF_BASE`; absence means vmlinux mode, presence means module mode. `gen_btf_data()` runs pahole into detached `.BTF.1`, then `resolve_btfids` to produce `.BTF` and related data. Vmlinux mode builds a relocatable `.btf.o`; module mode objcopies `.BTF` and optional `.BTF.base`/`.BTF_ids` into the module and patches IDs.

## State and Persistence Behavior
It writes temporary and final files adjacent to the ELF. `trap cleanup EXIT` removes intermediate `.BTF.1`, `.BTF`, and module-only side files, leaving vmlinux `.btf.o`/`.BTF_ids` or modified module ELF.

## Dependencies and Integration Points
Consumed by kernel build/link flows, especially `link-vmlinux.sh` and module post-processing. It depends on pahole, resolve_btfids, objcopy, compiler, and config auto.conf.

## Risks and Test Signals
Big-endian ET_REL patching writes raw ELF header bytes and must stay correct. Module mode mutates the input ELF. Test vmlinux and module paths, big-endian config, missing `.BTF_ids`, and verbose build logging.
