# sources/distributed-fs/openafs/src/afs/AIX/osi_assem.s

Purpose: RS/6000 assembly helper file for AIX kernel integration.

Important APIs and functions: exports `get_toc`, which copies register 2 into return register 3 to expose the current TOC pointer, and `get_ret_addr`, which walks the caller stack frame to return the saved link register.

Control flow: each function is a short leaf routine followed by AIX traceback tags and descriptor csects.

State and persistence: no mutable state. It only observes processor registers and stack frame layout.

Dependencies and integration: used by `osi_config.c` during kernel import setup, especially `kluge_init`, which needs the TOC for `import_kvar`.

Risks and test signals: correctness depends on AIX calling conventions, stack frame layout, and descriptor format. Build/link success and successful kernel symbol import are the practical tests.
