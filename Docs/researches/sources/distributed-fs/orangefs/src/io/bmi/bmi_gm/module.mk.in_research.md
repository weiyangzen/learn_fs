<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in

Purpose: Makefile fragment that adds the GM BMI transport sources to OrangeFS builds when configure enables GM support.

Important APIs, types, and functions: Under `ifneq (,$(BUILD_GM))`, it sets `DIR := src/io/bmi/bmi_gm`, lists `bmi-gm-addr-list.c`, `bmi-gm-bufferpool.c`, and `bmi-gm.c`, expands them into `src`, and appends them to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`. It also sets `MODCFLAGS_$(DIR)` with GM include paths and `-DENABLE_GM_BUFPOOL`.

Control flow and state: Build-system conditional only; no runtime behavior. The selected source list determines whether `bmi_gm_ops` is compiled into relevant libraries/servers.

Dependencies and integration points: Consumes configure substitutions `BUILD_GM` and `@GM_INCDIR@`. Integrates with the top-level OrangeFS make system through aggregate source variables.

Risks and test signals: The fragment always defines `ENABLE_GM_BUFPOOL` for this directory, so code paths for other GM buffering strategies are not built through this default path. Build tests should run configure with and without GM, verify include path substitution, and confirm all GM objects are linked where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in -->
