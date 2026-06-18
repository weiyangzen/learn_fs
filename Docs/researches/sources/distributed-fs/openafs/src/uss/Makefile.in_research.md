
# sources/distributed-fs/openafs/src/uss/Makefile.in

This makefile builds the `uss` user/account provisioning tool and its lex/yacc parser. It compiles core modules for procedures, common utilities, volume creation, ACLs, ptserver, kauth, fs interactions, plus generated `lex.yy.o` and `y.tab.o`, and links against kauth, volser, cmd, and opr libraries.

Generated parser flow is explicit: `lex.yy.c` is produced from `lex.l`, then transformed by `yy-lsed`; `y.tab.c` and `y.tab.h` are produced from `grammar.y` and also transformed by `yy-lsed`. Special CFLAGS are used for generated lexer code to suppress unused/old-style/implicit-fallthrough warnings. Install places `uss` under `sbindir`; dest places it under legacy `/etc`.

Dependencies reflect the parser and module coupling: `uss.c` depends on common/procs/kauth/fs headers; procedure modules depend on ACL, volume, common, and fs headers. Persistence is build/install artifact generation only.

Risks include generated-file sed post-processing, yacc/lex tool differences, generated header ordering (`lex.yy.o` depends on `y.tab.c`), and broad static link dependencies. Test signals are clean parser regeneration, full `uss` link, install/dest staging, and parser smoke tests with sample bulk/template files.
