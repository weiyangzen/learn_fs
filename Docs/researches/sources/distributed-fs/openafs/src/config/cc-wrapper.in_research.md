# sources/distributed-fs/openafs/src/config/cc-wrapper.in

Purpose: shell wrapper around compiler and linker invocations that optionally adds CTF debug type conversion/merging.

Important APIs/types/functions: accepts `cc` or `ld` mode followed by the real command, substitutes `CTFCONVERT`, `CTFMERGE`, `RM`, and `AFS_SYSNAME`, parses `-o` and `-g`, honors `OPENAFS_CC_WRAPPER_DEBUG_FLAG`, and defines helper functions `echo_run` and `cleanup`.

Control flow: runs the wrapped command first. If CTF tools are unavailable or no debug flag is present, exits successfully. For compile mode it optionally skips empty Solaris 11.1 objects after `elfdump`, then runs `ctfconvert`. For link mode it gathers `.o`/`.a` inputs, converts the executable itself if needed, and runs `ctfmerge`. Errors trigger cleanup of the target.

State and persistence: mutates only the build target by adding CTF data or removing it on post-processing failure. No persistent config is written.

Dependencies and integration: configured into `CC_WRAPPER` and `LD_WRAPPER` in `Makefile.config`; integrates Solaris CTF tools with OpenAFS builds.

Risks and test signals: risks are shell quoting for unusual paths, target extraction failures, Solaris-specific `elfdump` assumptions, and missing `.o/.a` detection for direct source links. Signals include debug and non-debug builds, Solaris kernel module builds, empty compilation units, and failure cleanup behavior.
