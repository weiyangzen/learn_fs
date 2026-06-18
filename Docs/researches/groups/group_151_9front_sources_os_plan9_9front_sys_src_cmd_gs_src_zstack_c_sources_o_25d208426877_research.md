# Group Research: group_151_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_zstack_c_sources_o_25d208426877

Scope: `Docs/research_subset_a.md`; source tree `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zstack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zstack.c

## Purpose
Implements core PostScript operand-stack operators for Ghostscript.

## Key Elements
Defines `pop`, `exch`, `dup`, `index`, `roll`, `clear`, `count`, `mark`, `cleartomark`, and `counttomark`. The public operator table is `zstack_op_defs`.

## Behavior/Risks
`index` and `roll` handle stack entries that may span older stack blocks through `ref_stack_index` and `ref_stack_count`. `roll` has optimized common cases for `1` and `-1`, and slower multi-block rotation for deep stack ranges. Range and stack checks are explicit and return PostScript errors such as `rangecheck`, `stackoverflow`, and `unmatchedmark`.

## Dependencies
Uses interpreter stack primitives from `istack.h`, allocation context from `ialloc.h`, operand macros from `oper.h`, and ref assignment/store helpers from `store.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zstring.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zstring.c

## Purpose
Implements Ghostscript string allocation, name-to-string conversion, and string search/match operators.

## Key Elements
Defines `.bytestring`, `string`, `.namestring`, `anchorsearch`, `search`, `.stringbreak`, and `.stringmatch`.

## Behavior/Risks
`string` allocates VM-managed strings with `ialloc_string` and enforces `max_string_size`; `.bytestring` allocates byte arrays as structures. `anchorsearch` and `search` return PostScript-style segmented string results with boolean success markers. `.stringbreak` searches for any byte from a delimiter string and explicitly handles embedded NUL bytes. `.stringmatch` supports string/name pattern matching and treats a one-character `*` pattern as matching non-string/name objects.

## Dependencies
Uses Ghostscript allocation, name, VM-space, operand, and store APIs plus `gsutil.h` for `string_match`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zstring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zsysvm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zsysvm.c

## Purpose
Adds non-standard Ghostscript operators for creating arrays, dictionaries, packed arrays, and strings in a selected VM space.

## Key Elements
Uses `specific_vm_op()` to temporarily switch allocation space around existing constructors. Exposes `.globalvmarray`, `.globalvmdict`, `.globalvmpackedarray`, `.globalvmstring`, corresponding local/system variants, and `.systemvmcheck`.

## Behavior/Risks
System VM is described as outside normal `save`/`restore` semantics and restricted to simple/system references. The implementation saves and restores the current allocator space around each delegated constructor, so failures propagate from the underlying `zarray`, `zdict`, `zpackedarray`, or `zstring`.

## Dependencies
Depends on VM-space allocation state from `ialloc.h`/`ivmspace.h`, generic constructors declared elsewhere, and ref-space checks from `store.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zsysvm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztoken.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztoken.c

## Purpose
Implements token-reading and token-execution operators for files and strings.

## Key Elements
Defines `token`, `.tokenexec`, exported continuation `ztokenexec_continue`, shared continuation logic, comment/DSC comment callout handling, and `ztoken_scanner_options()` for user-parameter driven scanner flags.

## Behavior/Risks
String tokenization uses `scan_string_token` and restores operand-stack depth on scanner errors. File tokenization uses heap-saved `scanner_state` records when refills or callouts suspend scanning. `.tokenexec` differs from `token exec` by leaving literal procedures literal while executable binary object sequences may execute. `%ProcessComment` and `%ProcessDSCComment` are looked up dynamically and called through the exec stack when enabled.

## Dependencies
Integrates with operand, exec, and dictionary stacks; stream/file APIs; scanner state and scanner options; dictionary lookup; and Ghostscript structured allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztoken.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrans.c

## Purpose
Implements PostScript/PDF transparency-related interpreter operators.

## Key Elements
Provides blend mode, opacity alpha, shape alpha, and text knockout getters/setters. Implements transparency group/mask begin/end/discard/init operators, ImageType 3x soft-mask image setup, and pdf14 transparency device filter push/pop.

## Behavior/Risks
Dictionary parsing validates required transparency keys such as `Subtype`, optional backgrounds, transfer functions, mask dictionaries, and interleave constraints. Transparency masks may use a Ghostscript function as a one-input/one-output transfer function. `image3x` rewires mask data sources before image data sources for interleaved soft masks. Discard operators range-check the current transparency state before dropping a layer.

## Dependencies
Uses graphics state transparency APIs from `gstrans.h`, color space APIs, image parameter parsing, function evaluation, dictionary parameter helpers, and pdf14 device support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrap.c

## Purpose
Provides minimal LanguageLevel 3 trapping parameter operators.

## Key Elements
Defines global `i_trap_params`, `.settrapparams`, and `settrapzone`.

## Behavior/Risks
The source marks the trap-parameter storage as bogus, and `settrapzone` is explicitly not implemented, returning `undefined`. `.settrapparams` reads a dictionary into a parameter list and delegates validation/application to `gs_settrapparams`.

## Dependencies
Uses dictionary parameter-list helpers from `iparam.h` and trap support from `gstrap.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztype.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztype.c

## Purpose
Implements PostScript type inspection, access attributes, executable/literal conversion, and scalar/string conversion operators.

## Key Elements
Defines `.type`, `.typenames`, `cvlit`, `cvx`, `xcheck`, `executeonly`, `noaccess`, `readonly`, `rcheck`, `wcheck`, `cvi`, `cvn`, `cvr`, `cvrs`, and `cvs`.

## Behavior/Risks
`cvx` rejects internal operators outside the exec stack. Access checks handle dictionaries through dictionary access refs and include special restrictions for permanent/read-only dictionaries. Numeric conversions parse strings through the scanner and enforce integer range with real bounds. `cvrs` handles radix 2 through 36 and reuses `cvs` logic for radix 10. `cvs` has a compatibility hack that truncates internal operator names beginning with `%`, `.`, or `@` on rangecheck.

## Dependencies
Uses scanner, name, dictionary stack, ref access flags, interpreter utility conversion routines, and object-to-string formatting from `iutil.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ztype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zupath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zupath.c

## Purpose
Implements Level 2 user path operators and insideness tests.

## Key Elements
Provides `infill`, `ineofill`, `instroke`, `inufill`, `inueofill`, `inustroke`, `uappend`, `ucache`, `ufill`, `ueofill`, `upath`, `ustroke`, and `ustrokepath`. Also exports `make_upath()` for building user path arrays from graphics paths.

## Behavior/Risks
Insideness tests install a hit-detection device after clipping either to a single device pixel around coordinates or to a supplied user path. User paths may be ordinary executable arrays or compact two-element encoded forms with numeric operands and opcode strings. The compact form supports repeat opcodes and validates argument counts against the user-path operator table. Optional matrices are supported for stroke operations. `ucache` is currently a no-op.

## Dependencies
Uses graphics path enumeration, clipping, path painting, path preservation, matrix parsing, binary number array decoding, dictionary lookup of executable path operators, and the Ghostscript hit-detection device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zupath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zusparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zusparam.c

## Purpose
Implements user and system parameter operators for Ghostscript.

## Key Elements
Defines `.setsystemparams`, `.currentsystemparams`, `.getsystemparam`, `.setuserparams`, `.currentuserparams`, `.getuserparam`, and Level 2 `.checkpassword`. Parameter definitions cover build/revision data, font cache limits, global/local VM limits, VM reclaim/threshold, stack limits, halftone/font flags, byte order, real format, and file-permission locking.

## Behavior/Risks
System parameter changes require the system-parameters password and may update stored start-job/system passwords. User parameter changes update cached scanner options through `ztoken_scanner_options`. Parameter setting is not transactional; the file explicitly notes it does not roll back earlier successful changes if a later parameter fails. String parameter setting is not implemented despite string current-parameter support.

## Dependencies
Touches font-directory cache APIs, memory GC status/configuration, stack limits, token scanner options, password helpers, dictionary parameter lists, and current interpreter context fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zusparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem.c

## Purpose
Implements core PostScript virtual-memory operators: `save`, `restore`, `vmstatus`, and Ghostscript extension `.forgetsave`.

## Key Elements
Defines `vm_save_t` to associate allocator save levels with saved graphics state. Public routines include `zsave`, `restore_check_save`, `dorestore`, `zrestore`, and `zvmstatus`.

## Behavior/Risks
`save` allocates a local VM save record, creates allocator save state, and saves graphics state. `restore` validates the save operand, scans operand/exec/dictionary stacks for objects newer than the save, fixes stack refs and executable empty strings/files, then iteratively restores allocator and graphics state. `.forgetsave` removes a save without restoring memory state by splicing graphics-state save chains and forgetting the allocator save. `dorestore` temporarily clears `LockFilePermissions` after restore so restored user parameters can be reapplied without invalid access.

## Dependencies
Uses allocator save internals, stack enumeration, graphics state save/restore, dictionary stack cache reload, file refs, and memory status APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem2.c

## Purpose
Implements Level 2 VM-space and garbage-collector control operators.

## Key Elements
Provides `.setglobal`, `.currentglobal`, `gcheck`, and Level 2 `.vmreclaim`. Exports `set_vm_threshold()` and `set_vm_reclaim()` for `setuserparams`.

## Behavior/Risks
`.setglobal` switches allocation between global and local VM. `gcheck` reports whether an object is not local. `set_vm_threshold` normalizes `-1` and clamps thresholds before setting global and local thresholds. `set_vm_reclaim` enables/disables GC independently for system/global/local spaces according to values `-2` through `0`. `.vmreclaim` forces interpreter exit via `e_VMreclaim` for immediate collection requests `1` or `2`.

## Dependencies
Uses VM-space macros from `ivmspace.h`, memory GC control via `ivmem2.h`, and operand/ref helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zvmem2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile

## Purpose
Builds the vendored zlib library and its sample programs.

## Key Elements
Defaults to `CC=cc`, `CFLAGS=-O`, static `libz.a`, and shared library names for zlib `1.2.2`. Builds objects for checksum, compression, inflate/deflate, trees, utility, and gzip I/O modules. Main targets include `all`, `test`, `libz.a`, optional shared library, `example`, `minigzip`, `install`, `uninstall`, `clean`, `distclean`, `tags`, and `depend`.

## Behavior/Risks
The default `all` target builds `example` and `minigzip`, not only the library. `test` pipes data through `minigzip` and runs `example`. Install copies headers, library, and man page into configurable prefixes. `Makefile` and `Makefile.in` are identical in this tree, so `distclean` restores this same template.

## Dependencies
Assumes a traditional Unix shell, `ar`, optional `ranlib`, compiler, and zlib source files in the same directory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile.in

## Purpose
Template Makefile used by the zlib `configure` script.

## Key Elements
Contains the same build variables, object lists, targets, install rules, clean rules, and generated dependency comments as `Makefile`.

## Behavior/Risks
`configure` rewrites selected assignment lines such as `CC`, `CFLAGS`, `CPP`, `LDSHARED`, `LIBS`, shared-library names, install paths, and `LDFLAGS` into `Makefile`. Since this checked-in `Makefile.in` already matches `Makefile`, it also serves as a reset target for `distclean`.

## Dependencies
Used by `configure` through `sed` substitution and by `make distclean` through `cp -p Makefile.in Makefile`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/adler32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/adler32.c

## Purpose
Implements zlib’s Adler-32 checksum.

## Key Elements
Defines `adler32()` with base prime `65521`, block size `NMAX`, unrolled byte accumulation macros, and optional `NO_DIVIDE` modular reduction.

## Behavior/Risks
A null buffer returns the Adler-32 initial value `1`. Input is processed in chunks sized to avoid 32-bit accumulator overflow, then sums are reduced modulo `BASE`. This is standard zlib checksum code from the vendored 1.2.2-era source.

## Dependencies
Includes `zlib.h` with `ZLIB_INTERNAL`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/adler32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/compress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/compress.c

## Purpose
Implements zlib’s convenience buffer compression APIs.

## Key Elements
Defines `compress2()`, `compress()`, and `compressBound()`.

## Behavior/Risks
`compress2` wraps `deflateInit`, `deflate(..., Z_FINISH)`, and `deflateEnd` around caller-provided buffers. It checks 16-bit `MAXSEG_64K` truncation and output buffer size truncation. If deflate does not reach stream end, it maps a continuing `Z_OK` to `Z_BUF_ERROR`. `compressBound` returns the classic zlib upper-bound formula for default settings.

## Dependencies
Uses public zlib stream API from `zlib.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/configure -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/configure

## Purpose
Hand-written zlib configuration script for compiler flags, shared-library support, install paths, and generated config files.

## Key Elements
Parses `--shared`, `--prefix`, `--exec_prefix`, `--libdir`, and `--includedir`. Detects zlib version from `zlib.h`, chooses compiler/linker flags for gcc and many Unix variants, tests shared library creation, probes `unistd.h`, printf-family availability and return values, `errno.h`, `mmap`, and assembler symbol underscores.

## Behavior/Risks
Writes temporary `ztest$$` files, generates `zconf.h` from `zconf.in.h`, and rewrites `Makefile` from `Makefile.in` using `sed`. If safe formatted-output APIs are unavailable, it adds fallback macros and prints warnings that builds may be vulnerable to string-format buffer overflow issues. The script is deliberately simple and not Autoconf-generated.

## Dependencies
Requires `/bin/sh`, `sed`, compiler/linker tools, `uname`, optional `nm`, and local `zlib.h`, `zconf.in.h`, and `Makefile.in`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.c

## Purpose
Implements zlib CRC-32 computation.

## Key Elements
Supports static CRC tables from `crc32.h` or optional `DYNAMIC_CRC_TABLE` generation. Exposes `get_crc_table()` and `crc32()`, with optimized little-endian and big-endian four-byte-at-a-time variants when `BYFOUR` is available.

## Behavior/Risks
The source warns that dynamic table generation is not protected by a mutex and should be initialized before multi-threaded use. Runtime endian detection dispatches to little/big optimized paths when pointer/integer assumptions match. Null input returns `0`. `MAKECRCH` mode can regenerate `crc32.h`.

## Dependencies
Uses `zutil.h`, optional `limits.h`, optional `stdio.h` in table-generation mode, and the generated `crc32.h` table in normal static-table builds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.h

## Purpose
Provides generated static lookup tables for fast CRC-32 calculation.

## Key Elements
Defines `crc_table[TBLS][256]` with the base 256-entry CRC table and additional `BYFOUR` tables for word-at-a-time big/little endian CRC paths.

## Behavior/Risks
This is generated data, not handwritten algorithmic code. Correctness depends on consistency with the polynomial/table-generation logic in `crc32.c`. The table is conditionally sized by `TBLS`, so it must be included in the same macro environment expected by `crc32.c`.

## Dependencies
Included only from `crc32.c`, relying on `local`, `FAR`, and `TBLS` being defined before inclusion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.c

## Purpose
Implements zlib’s DEFLATE compressor.

## Key Elements
Defines public compression APIs including `deflateInit_`, `deflateInit2_`, `deflateSetDictionary`, `deflateReset`, `deflatePrime`, `deflateParams`, `deflateBound`, `deflate`, `deflateEnd`, and `deflateCopy`. Internal compression engines include stored blocks, fast compression, and slow/lazy compression.

## Behavior/Risks
Uses a sliding LZ77 window, hash chains, level-dependent configuration table, optional gzip wrapper support, Adler-32/CRC-32 trailer handling, and Huffman block flushing via `trees.c` helpers. It handles partial output buffers by leaving pending output and returning `Z_OK` until the caller provides more space. `deflateParams` may flush before switching compression functions. `deflateCopy` duplicates internal state except on 16-bit segmented builds. The implementation contains many portability branches for old compilers and 16-bit constraints.

## Dependencies
Depends on internal structures/macros from `deflate.h`, checksum functions, zlib allocator hooks, tree/Huffman helper functions, and zlib public stream semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.h

## Purpose
Defines zlib’s private compressor state and internal compression constants.

## Key Elements
Declares literal/length/distance code constants, stream status values, Huffman tree data structures, `Pos`/`IPos`, and the full `deflate_state` structure. Declares tree helper functions and inline tally macros for literals and distance/length pairs.

## Behavior/Risks
The header explicitly warns applications not to include it directly. `deflate_state` owns the sliding window, hash chains, pending output, compression parameters, dynamic Huffman trees, match buffers, heap, and bit buffer. Macro-heavy design ties it tightly to `deflate.c` and `trees.c`, with behavior changing under `DEBUG`, `FASTEST`, `NO_GZIP`, and related compile-time flags.

## Dependencies
Includes `zutil.h` and expects zlib internal types, allocation, and portability macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/deflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/example.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/example.c

## Purpose
Sample and regression test program for the vendored zlib API.

## Key Elements
Tests `compress`/`uncompress`, gzip file I/O, small-buffer deflate/inflate, large-buffer compression with dynamic parameter changes, full flush and `inflateSync`, and preset dictionary deflate/inflate.

## Behavior/Risks
The program exits on first failure through `CHECK_ERR` or explicit validation checks. It creates a gzip test file named `foo.gz` or platform variant, corrupts part of a compressed stream to test sync recovery, and verifies preset dictionary IDs via Adler-32. It allocates large cleared buffers so repeated data compresses predictably.

## Dependencies
Uses public `zlib.h`, standard C I/O/string/allocation headers where available, gzip APIs, deflate/inflate APIs, and filesystem access for the gzip test file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/example.c -->