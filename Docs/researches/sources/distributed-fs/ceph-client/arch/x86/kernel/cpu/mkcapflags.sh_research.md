# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mkcapflags.sh

Purpose: generates C string arrays for x86 CPU feature, bug, and optional VMX feature names from preprocessor definitions in header files. The output is used by CPU information reporting paths so feature bits can be rendered as stable lowercase names.

Important APIs/types/functions: shell function `dump_array ARRAY SIZE PFX POSTFIX IN` emits a `const char * const` array. It parses `#define` lines for prefixes such as `X86_FEATURE_`, `X86_BUG_`, and `VMX_FEATURE_`, extracts quoted comments as user-facing names, lowercases them, and prints designated initializers. The script writes to positional output `$1` using input headers `$2` and `$3`.

Control flow: `set -e` aborts on errors. A trap removes the output file on failure. The script emits `cpufeatures.h`, calls `dump_array` for `x86_cap_flags`, calls it again for `x86_bug_flags` using `NCAPINTS*32` as an index offset postfix, then conditionally emits VMX feature names behind `CONFIG_X86_VMX_FEATURE_NAMES`.

State and persistence: writes exactly one generated output file passed as `$1`. It reads the feature definition headers and has no other persistent state.

Dependencies and integration points: depends on POSIX shell utilities `sed`, `tr`, `wc`, `printf`, and arithmetic expansion. It integrates with the kernel build system as a generator for architecture CPU flag name arrays and relies on quoted comments in `cpufeatures.h` and `vmxfeatures.h`.

Risks: parsing is format-sensitive; feature defines without quoted comments are skipped. Spacing and tab calculations affect readability but not semantics. Missing arguments can cause confusing shell failures. Since values are lowercased blindly, comments must already encode the desired public token.

Test signals: run the generator against representative cpufeatures/vmxfeatures headers, compile the generated C, verify indexes for normal features and bug offsets, check skipped unquoted comments, and compare `/proc/cpuinfo` flag names against expected strings.
