# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Makefile

Purpose: top-level kbuild dispatcher for Samsung media platform driver subdirectories.

Important APIs and entries: unconditionally descends into `exynos-gsc/`, `exynos4-is/`, `s3c-camif/`, `s5p-g2d/`, `s5p-jpeg/`, and `s5p-mfc/` using `obj-y +=`.

Control flow: kbuild visits each subdirectory; each child Makefile decides whether objects are built based on its Kconfig symbols.

State and persistence: no runtime state. Build output is controlled by child `obj-$(CONFIG_...)` rules.

Dependencies and integration points: must stay aligned with top-level Samsung Kconfig and actual child directories. It is the path by which the exynos-gsc Makefile participates in kernel builds.

Risks: unconditional directory descent is standard but means stale or missing child directories cause build failures. New subdrivers need both Kconfig and Makefile updates.

Test signals: `make drivers/media/platform/samsung/` with different Samsung media configs and allmodconfig.
