# sources/distributed-fs/ceph-client/drivers/media/platform/st/Makefile

Purpose: includes ST media platform child directories in kbuild.

Important APIs and entries: unconditionally adds `sti/bdisp/`, `sti/delta/`, `sti/hva/`, and `stm32/` to `obj-y`.

Control flow: kbuild descends into these directories, where child Makefiles decide actual objects based on Kconfig symbols.

State and persistence: no runtime state. It controls build traversal only.

Dependencies and integration points: links the top-level ST media platform directory to STI and STM32 media drivers.

Risks: unconditional descent is normal but requires each child directory to be build-safe when its symbols are disabled. Missing a new child directory here would prevent its Makefile from being evaluated.

Test signals: kbuild traversal in disabled and enabled configurations; allmodconfig; and `make M=drivers/media/platform/st`.
