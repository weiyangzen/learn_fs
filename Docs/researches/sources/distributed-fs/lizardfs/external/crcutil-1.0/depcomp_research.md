<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp

## Purpose
`depcomp` is the Automake dependency-compilation wrapper bundled with crcutil. It runs a compiler command while also producing a make-readable dependency file for the compiled source, normalizing many compiler-specific dependency formats into Automake's expected `.P*` files.

## Important inputs and modes
The script requires environment variables `depmode`, `source`, and `object`; it optionally uses `DEPDIR`, `depfile`, `tmpdepfile`, and `libtool`. With no command it errors; `--help` and `--version` print metadata. If `depfile` is unset, it maps an object like `sub/bar.o` to `sub/.deps/bar.Po`; if `tmpdepfile` is unset, it derives a temporary `.T*` file.

Supported modes include `gcc3`, `gcc`, `hp`, `sgi`, `aix`, `icc`, `hp2`, `tru64`, `dashmstdout`, `dashXmstdout`, `makedepend`, `cpp`, `msvisualcpp`, `msvcmsys`, and `none`. Some modes are aliases or markers used by Automake's `depend.m4`, such as `hp`, `dashXmstdout`, and `msvcmsys`.

## Control flow
The preamble validates required variables, computes output paths, removes stale temporary dependency files, and normalizes alias modes. The large case dispatch then executes the compiler command with mode-specific dependency flags or, for slower modes, runs the compile first and then derives dependencies through preprocessor output or `makedepend`.

For GCC-like modes it uses `-MD`, `-MP`, `-MF`, or `-Wp` flags and then rewrites the dependency file so the target is the requested object and every header also has a dummy `header:` rule. Vendor modes handle dependency files emitted in unusual locations, including AIX `.u`, HP `.d`, Tru64 `.o.d`, libtool `.libs` paths, and Intel compiler output. Preprocessor-based modes remove libtool wrappers and `-o object` arguments before extracting included file paths from stdout. `none` simply execs the compiler command without dependency generation.

## State and persistence behavior
The persistent output is `depfile`, usually under `.deps`, containing an object dependency rule plus dummy header rules to avoid deleted-header make failures. The script creates and removes `tmpdepfile` and compiler-specific temporary dependency outputs. On compiler failure, it deletes temporary files and exits with the compiler status. It does not maintain long-lived state outside generated dependency files.

## Dependencies and integration points
`depcomp` is called from Automake-generated `Makefile` rules selected by `configure`'s dependency-mode probes. It depends on a POSIX shell plus standard tools such as `sed`, `tr`, `sort`, `grep`, and optionally `cygpath` and `makedepend`. It integrates with libtool compile wrappers when `libtool=yes` and with make include syntax detected during configuration.

## Risks and edge cases
Dependency mode detection is compiler-specific and conservative; a compiler that accepts unknown flags with warnings can produce false positives, so configure greps stderr for Intel ignored-option messages. Path handling must account for DOS drive letters, spaces, object files in subdirectories, and libtool's `.libs` outputs. The generated dependency file can become stale if a compiler writes dependencies somewhere unexpected. Manual edits should be avoided because Automake may replace this file.

## Test signals
The strongest test is `./configure` dependency-style detection followed by a normal `make` with dependency tracking enabled. Inspect `.deps/*.Po` or `.Plo` files to ensure they reference the expected object and included headers. Rebuild after deleting a header from a dependency file to verify dummy header rules avoid make parse failures. Also validate `--disable-dependency-tracking`, which should bypass this wrapper for normal builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp -->
