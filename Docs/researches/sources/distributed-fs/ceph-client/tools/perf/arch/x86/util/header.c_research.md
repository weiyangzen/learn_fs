# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/header.c

Purpose: This file implements x86 CPUID string generation and matching for perf headers, PMU event table selection, metric expressions, and architecture-specific feature dispatch.

Important APIs, types, and functions: `get_cpuid_0()` reads CPUID leaf 0 and formats the vendor string. `__get_cpuid()` is the shared formatter for vendor, family, model, and stepping. `get_cpuid()` emits `vendor,family,model,step` for perf metadata. `get_cpuid_str()` allocates and returns `vendor-family-model-stepping`, with model and stepping in hex formatting. `is_full_cpuid()` checks whether a CPUID pattern contains three dashes. `strcmp_cpuid_str()` compiles the map CPUID as an extended regex and returns 0 only for an accepted full-string match.

Control flow: `__get_cpuid()` always reads vendor/largest basic leaf, conditionally reads leaf 1 for family/model/stepping, applies Intel/AMD extended-family and extended-model rules, then writes into a caller buffer using a sentinel `$` at the end of the format. If the sentinel fits, it is removed and success is returned; otherwise `ENOBUFS` is returned. `strcmp_cpuid_str()` rejects incomplete runtime IDs when a full map CPUID is required, rejects invalid regexes, executes the regex, adjusts match length to ignore stepping when the map pattern is not full but the runtime ID is full, and returns 0 only if the match covers the intended full length.

State and persistence: `get_cpuid_str()` allocates a 128-byte string that callers must free. Other functions write into caller-provided buffers. No persistent state is stored.

Dependencies and integration points: It depends on the inline CPUID wrapper in `cpuid.h`, perf debug logging, regex APIs, and weak generic header hooks in `util/header.c`. PMU event code, metric expressions, AUX tracing, and x86 PMU utilities use these functions to identify CPU-specific tables and capabilities.

Risks: The sentinel-fit check depends on `scnprintf()` writing the trailing `$`; if formatting changes, truncation detection can break. `strcmp_cpuid_str()` treats map strings as regexes, so unescaped metacharacters are meaningful. Full CPUID enforcement prevents ambiguous platform selection but can reject incomplete environment overrides. Family/model extraction must stay consistent with x86 CPUID rules.

Test signals: PMU event table lookup should select the expected x86 CPU map. Expression tests using `strcmp_cpuid_str()` should pass. `perf report --header` or debug output should show stable x86 CPUID strings, and invalid CPUID regexes should produce informative `pr_info()` messages.
