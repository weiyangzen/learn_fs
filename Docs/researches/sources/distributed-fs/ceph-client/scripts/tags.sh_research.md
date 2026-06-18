# sources/distributed-fs/ceph-client/scripts/tags.sh

Purpose: `tags.sh` generates source navigation databases for the kernel tree: ctags `tags`, etags `TAGS`, GNU GLOBAL `gtags`, or cscope files.

Important APIs, types, and functions: source discovery helpers include `find_arch_sources()`, `find_arch_include_sources()`, `find_include_sources()`, `find_other_sources()`, `all_sources()`, `all_compiled_sources()`, `all_target_sources()`, and `all_kconfigs()`. Generators include `docscope()`, `dogtags()`, `setup_regex()`, `exuberant()`, `emacs()`, and `xtags()`. Large regex arrays teach taggers kernel macro-generated symbols for assembly, C, and Kconfig.

Control flow: the script builds ignore expressions from `RCS_FIND_IGNORE`, `*.mod.c`, and `IGNORE_DIRS`; selects source-root path style from `srctree`, `KBUILD_ABS_SRCTREE`, and gtags constraints; resolves `ALLSOURCE_ARCHS`; handles UML `SUBARCH`; then dispatches by mode. For tags/TAGS it removes previous output, runs the best supported tagger mode, and removes struct forward-declaration tags with sed.

State and persistence: writes `tags`, `TAGS`, `GTAGS`/GLOBAL files, `cscope.files`, and `cscope.out` depending on mode.

Dependencies and integration points: invoked by Kbuild developer targets. Depends on bash arrays, find, awk, grep, sed, xargs, realpath, ctags/etags/gtags/cscope, and kernel build `.cmd` files when `COMPILED_SOURCE` is set.

Risks: find expression construction uses shell-expanded ignore strings and requires trusted inputs. Very large trees can stress command-line length through `xargs`, though xargs mitigates. Regex compatibility differs between universal/exuberant/emacs taggers.

Test signals: generate each mode in in-tree and O= builds, with `ALLSOURCE_ARCHS=all`, `COMPILED_SOURCE=1`, UML arch, and both universal and emacs ctags.
