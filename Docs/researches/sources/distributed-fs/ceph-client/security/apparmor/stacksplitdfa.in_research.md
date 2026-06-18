# sources/distributed-fs/ceph-client/security/apparmor/stacksplitdfa.in

Purpose: static serialized AppArmor DFA input used for stack-splitting/name parsing behavior, with the leading comment documenting the source pattern `0x1 [^\000]*[^/\000]//&`.

Important APIs, types, and functions: no C APIs or functions. The file is a byte table consumed by AppArmor build-time or generated-DFA include machinery alongside other `.in` DFA blobs.

Control flow: none at runtime in this file; consumers treat the bytes as a compiled DFA. The encoded automaton appears to detect hierarchical namespace/profile split markers involving `"//"` after non-slash content.

State and persistence: immutable source artifact. Runtime state is whatever DFA object the build/include path creates from these bytes.

Dependencies and integration: integrates with AppArmor DFA unpack/match code and build rules that embed generated DFA data. It is related to name parsing, stack splitting, and namespace/profile separators.

Risks and test signals: hand-maintained byte blobs are opaque; corruption may not be obvious until matching behavior changes. Test signals are successful DFA unpacking and policy-name parsing cases around empty components, slash boundaries, and `"//"` split markers.
