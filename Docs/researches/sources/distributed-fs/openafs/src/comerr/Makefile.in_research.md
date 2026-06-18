# sources/distributed-fs/openafs/src/comerr/Makefile.in

Purpose: builds the OpenAFS com_err runtime library and the `compile_et` build tool used to generate error table source/header files.

Important targets: `all` builds `compile_et`, installs public headers, builds `libafscom_err.a`, `liboafs_comerr.la`, and `libcomerr_pic.la`. `et_lex.lex.c` is generated from `et_lex.lex.l`; `compile_et` links `compile_et.o` and yacc output `error_table.o`, with platform-specific lex library handling. Install targets place `afs_compile_et`, headers, and library artifacts.

Dependencies and integration: includes config/LWP/lwptool fragments and links against `opr` and roken. Many OpenAFS components depend on `compile_et` during generated-header phases and on `libafscom_err` at runtime.

Risks and tests: generated parser/lexer files must be available and compatible with local lex/yacc. Platform case logic is hand-maintained. `test` delegates to a subdirectory not covered by this work item.
