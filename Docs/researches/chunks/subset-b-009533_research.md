# sources/test-tools/xfstests-bld/fstests-bld/popt/configure lines 17883-18807

## Purpose

This chunk is the tail of the generated GNU Autoconf/libtool `configure` script for the embedded `popt` package. It finishes emitting the generated `libtool` script, handles gettext PO directory Makefile generation inside `config.status`, runs `config.status` unless creation was disabled, recurses into configured subdirectories, and finally warns about unrecognized options.

The range begins inside the `config.status` case that writes libtool configuration into a temporary `$cfgfile` and ends after recursive sub-configuration has completed. It does not contain application logic for `popt` itself; its purpose is to persist probe results from earlier configure checks into generated build artifacts.

## High-Level Structure

- Lines 17883-18231: Writes the `# ### BEGIN LIBTOOL CONFIG` block into the generated libtool script. The block serializes libtool variables computed earlier by configure, including host/build identities, compiler/linker/archive tools, shared/static library policy, symbol extraction commands, rpath behavior, PIC/static flags, and module/archive commands.
- Lines 18235-18247: Adds an AIX 3.x compatibility stanza that initializes and exports `COLLECT_NAMES` when missing, working around historical GCC `collect2` behavior.
- Lines 18250-18464: Builds the final `libtool` script from `$ac_aux_dir/ltmain.sh`. It appends the prefix of `ltmain.sh`, injects shell helper functions chosen according to `$xsi_shell` and `$lt_shell_append`, appends the remainder of `ltmain.sh`, atomically moves `$cfgfile` to `$ofile` when possible, and marks the output executable.
- Lines 18467-18579: Handles the `po-directories` `config.status` tag. For each configured `*/Makefile.in`, it detects gettext PO directories by `POTFILES.in`, creates `POTFILES`, computes language-derived variables such as `POFILES`, `GMOFILES`, and `CATALOGS`, generates the PO `Makefile`, and appends applicable `Rules-*` fragments.
- Lines 18581-18593: Closes the `config.status` tag loop and heredoc, marks `$CONFIG_STATUS` executable, restores cleanup state, and aborts if writing `config.status` failed.
- Lines 18596-18615: Runs `$CONFIG_STATUS` unless `--no-create` was requested. It redirects fd 5 away from `config.log` while `config.status` runs to avoid DOS file-handle issues, then reopens fd 5 on `config.log`.
- Lines 18617-18802: Implements `CONFIG_SUBDIRS` recursion unless `--no-recursion` was requested. It filters unsuitable top-level configure arguments, prepends `--prefix`, `--silent`, and `--disable-option-checking`, creates build subdirectories, computes source/build path variables, locates each subdirectory configure script, and executes it with a correctly relative cache file and `--srcdir`.
- Lines 18803-18807: Emits a final warning for accumulated unrecognized options when option checking remains enabled.

## Important Generated APIs And Variables

- `CONFIG_STATUS` names the generated `config.status` script. This chunk writes, chmods, and optionally executes it.
- `$cfgfile` and `$ofile` are the temporary and final paths used while generating `libtool`; `$ltmain` is set to `$ac_aux_dir/ltmain.sh`.
- Serialized libtool configuration variables include `macro_version`, `macro_revision`, `build_libtool_libs`, `build_old_libs`, `pic_mode`, `fast_install`, `host`, `host_os`, `build`, `build_os`, `SED`, `GREP`, `NM`, `LN_S`, `AR`, `RANLIB`, `LTCC`, `LTCFLAGS`, `global_symbol_pipe`, `objdir`, `SHELL`, `ECHO`, `need_locks`, Darwin tools, library naming specs, rpath/hardcode controls, `LD`, `CC`, `wl`, `pic_flag`, `archive_cmds`, `module_cmds`, `export_symbols_cmds`, `prelink_cmds`, and `hardcode_action`.
- Injected libtool shell helpers are the runtime API consumed by `ltmain.sh`: `func_dirname`, `func_basename`, `func_dirname_and_basename` on XSI shells, `func_stripname`, `func_opt_split`, `func_lo2o`, `func_xform`, `func_arith`, `func_len`, and `func_append`.
- `CONFIG_FILES` drives the PO directory pass. Entries may use Autoconf's `outfile:infile...` syntax, so the handler strips suffix inputs before matching `*/Makefile.in`.
- gettext variables computed here include `POTFILES`, `POMAKEFILEDEPS`, `ALL_LINGUAS`, `POFILES`, `UPDATEPOFILES`, `DUMMYPOFILES`, `GMOFILES`, `INST_LINGUAS`, and `CATALOGS`.
- Recursive configuration uses `subdirs`, `ac_configure_args`, `prefix`, `silent`, `cache_file`, `srcdir`, `ac_aux_dir`, `ac_pwd`, `ac_top_build_prefix`, `ac_srcdir`, and `ac_sub_configure_args`.

## Control Flow

1. The libtool generation branch appends a literal configuration section to `$cfgfile`. Most assignments are copied from `lt_*`, `enable_*`, and platform variables computed earlier, so no new probing happens in this range.
2. If `host_os` matches `aix3*`, it appends a small environment compatibility block for `COLLECT_NAMES`.
3. The script reads `$ac_aux_dir/ltmain.sh` in two parts. First, it copies through the `# Generated shell functions inserted here` marker. It then emits optimized XSI-shell helpers or portable Bourne/sed/expr helpers, emits the best available `func_append` implementation, and finally copies from the marker to the end of `ltmain.sh`.
4. It finalizes the generated libtool file by moving `$cfgfile` over `$ofile`, falling back to copy/remove if `mv -f` fails, then applies executable permissions.
5. In the `po-directories` tag, the script iterates over `CONFIG_FILES`, narrows to Makefile inputs, derives the associated source directory, and only treats it as a PO directory when `POTFILES.in` exists.
6. For PO directories, it strips comments and blank lines from `POTFILES.in`, prefixes source paths, and computes language variables from `LINGUAS` when present or from obsolete configure-time `ALL_LINGUAS` state otherwise.
7. It filters installed catalogs through the user's `LINGUAS` environment value when set. A requested language variant can select a base present language by prefix match.
8. It generates the PO `Makefile` by applying sed replacements to `Makefile.in`, then appends non-backup `Rules-*` fragments from the source directory.
9. After the `config.status` script is written and marked executable, configure runs it unless `no_create=yes`. Failure of `config.status` fails configure.
10. If recursion is enabled, configure reconstructs a sanitized argument list for each subdirectory. It removes top-level cache/srcdir/prefix option forms that must be recomputed, quotes single quotes, prepends `--prefix`, optionally prepends `--silent`, and prepends `--disable-option-checking`.
11. For each configured subdirectory present in the source tree, it creates the matching build directory, calculates relative and absolute source/build paths, enters the build directory, selects `configure.gnu`, `configure`, or a Cygnus-style fallback via `$ac_aux_dir/configure`, and runs it through `eval` so the quoted argument list is honored.
12. The script returns to the original build directory after each sub-configure and emits a final unrecognized-option warning if configured to do so.

## State And Persistence Behavior

- The primary persistent outputs are the generated `libtool` script at `$ofile`, the generated `config.status` script at `$CONFIG_STATUS`, gettext PO helper files such as `$ac_dir/POTFILES`, generated PO `Makefile`s, and recursively generated outputs in any configured subdirectories.
- The generated libtool file persists earlier probe state by embedding shell variable assignments rather than re-running checks. A stale or incorrect earlier probe value becomes executable build policy in `libtool`.
- PO Makefile generation overwrites `$ac_dir/POTFILES` and `$ac_dir/Makefile` when a PO directory is detected. It reads source-side `POTFILES.in`, optional `LINGUAS`, optional `Makevars`, and source-side `Rules-*` files.
- `config.log` remains the central diagnostic log. This chunk temporarily redirects fd 5 to `/dev/null` while invoking `config.status`, then reopens it in append mode afterward.
- `ac_clean_files` is restored from `ac_clean_files_save` after writing `config.status`; write failures are tracked through `ac_write_fail`.
- Recursive configuration mutates process state by `cd`ing into each build subdirectory but restores `cd "$ac_popdir"` after each iteration. Each subconfigure may write its own `config.log`, `config.status`, Makefiles, caches, and generated headers under that subdirectory.

## Dependencies And Integration Points

- Depends on Autoconf/libtool support files, especially `$ac_aux_dir/ltmain.sh`; absence or unreadability of `ltmain.sh` causes libtool generation to fail and removes the temporary file.
- Depends on portable shell tools: `sed`, `cat`, `mv`, `cp`, `rm`, `chmod`, `mkdir`, `pwd`, and the selected `$SHELL`.
- Integrates with libtool by producing a runnable script that `Makefile`s later call through `LIBTOOL='$(SHELL) $(top_builddir)/libtool'`.
- Integrates with gettext/Automake PO directory layout through `POTFILES.in`, `LINGUAS`, `Makevars`, `Rules-*`, and `po/Makefile.in`-style templates.
- Integrates with recursive Autoconf projects through `CONFIG_SUBDIRS`/`subdirs`, supporting both in-tree and separate build trees and forwarding cache and source directory locations to nested configure scripts.
- Honors user-facing configure controls from earlier parsing: `--no-create`, `--no-recursion`, `--silent`, `--prefix`, `--cache-file`, `--srcdir`, `--disable-option-checking`, and the `LINGUAS` environment variable.

## Risks And Edge Cases

- This is generated script content; direct edits are likely to be overwritten by regenerating from `configure.ac`, gettext, Automake, and libtool macros.
- Libtool output correctness depends entirely on prior probe variables. Bad cached `lt_cv_*` or `ac_cv_*` values can be serialized into a working-looking but incorrect `libtool`.
- The `$ltmain` split relies on the exact marker `# Generated shell functions inserted here`. A mismatched `ltmain.sh` version can produce a malformed libtool script or duplicate/missing helper definitions.
- The recursive configure invocation uses `eval` to preserve quoting. The code escapes single quotes in forwarded arguments, but argument construction remains sensitive to shell quoting bugs and unusual option values.
- PO directory generation assumes language names and file lists are shell/sed friendly. Unexpected whitespace or shell metacharacters in `LINGUAS`, `POTFILES.in`, or directory names could affect generated variables or commands.
- The fallback directory creation path constructs and evaluates `mkdir $as_dirs`; unusual pathnames with embedded newlines or hard shell metacharacters can be risky despite single-quote handling.
- On DOS-like platforms, file descriptor handling around `config.log` is explicitly delicate. If fd 5 cannot be reopened or `config.status` output is lost, diagnosis becomes harder.
- The final unrecognized-option warning happens after outputs and sub-configures have already been generated, so it is advisory unless earlier option-checking settings made unknown options fatal.

## Test Signals

- A successful run should leave an executable `libtool` script containing a `# ### BEGIN LIBTOOL CONFIG` section and generated `func_*` helpers from this range.
- `config.status` should exist, be executable, and run successfully unless configure was invoked with `--no-create`.
- `config.log` should show the `config.status` invocation and, for recursive packages, messages like `=== configuring in <subdir>` and the exact nested configure command.
- For PO-enabled configurations, generated PO directories should contain refreshed `POTFILES` and `Makefile` files with `@POFILES@`, `@GMOFILES@`, `@CATALOGS@`, and related substitutions resolved.
- Recursive configure validation should check that relative `--cache-file` paths are adjusted with `ac_top_build_prefix`, `--srcdir` points to the correct source subdirectory, and failures in nested configure scripts abort the top-level configure.
- Useful focused tests are full `popt` configure runs with default options, `--no-create`, `--no-recursion`, `--silent`, a relative `--cache-file`, a non-default `--prefix`, and gettext-oriented `LINGUAS` values, followed by inspection of generated `libtool`, `config.status`, PO Makefiles, and `config.log`.
