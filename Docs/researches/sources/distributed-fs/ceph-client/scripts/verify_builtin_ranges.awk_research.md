# sources/distributed-fs/ceph-client/scripts/verify_builtin_ranges.awk

Purpose: `verify_builtin_ranges.awk` verifies that `modules.builtin.ranges` correctly maps built-in module address ranges to symbols in `System.map` and linker maps.

Important APIs, types, and functions: `get_module_info()` reads object-specific `.cmd` files to recover `DKBUILD_MODFILE` or `RUST_MODFILE`, validates single-module names against `modules.builtin`, caches results, and normalizes module names. `addr2val()` converts kernel hex addresses to AWK numeric values by stripping high bits when needed. Main processing uses `ARGIND` phases for ranges, System.map annotation, built-in module list, vmlinux.map, and optional vmlinux.o.map.

Control flow: phase 1 stores ranges. Phase 2 walks System.map symbols, advancing current range and recording `addr-name -> module` annotations. Phase 3 loads built-in modules. Phases 4/5 parse GNU ld or LLD map formats, identify sections/objects/symbols, handle `vmlinux.o` fallback, apply section addends, compare symbol module annotations against object module membership, and count matches, mismatches, and missing records. END prints a summary and exits nonzero on mismatch/missing.

State and persistence: no writes; it reads several generated build artifacts and object `.cmd` files. It caches module info and address annotations in AWK arrays.

Dependencies and integration points: used in kernel build validation for built-in module range metadata. Requires GNU awk features such as `ARGIND` and `strtonum`, plus linker map formats from GNU ld or LLD.

Risks: linker map parsing is necessarily format-sensitive. Address truncation assumes all kernel addresses lie in the same high region. Missing `.cmd` files cause a diagnostic suggesting running from the object directory for O= builds. Duplicate symbols can complicate classification.

Test signals: generated fixture maps for GNU ld and LLD, O= builds, Rust module objects, vmlinux.o fallback, duplicate symbols, zero-size boundary symbols, and intentionally corrupted range data.
