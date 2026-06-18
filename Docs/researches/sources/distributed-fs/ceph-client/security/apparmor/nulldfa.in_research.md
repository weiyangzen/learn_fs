# sources/distributed-fs/ceph-client/security/apparmor/nulldfa.in

Purpose: provides a compiled binary DFA byte array included by `lsm.c` as the built-in null policy automaton.

Important content: the file is a comma-separated hexadecimal byte stream, 8-byte aligned by the including C declaration. It begins with the AppArmor DFA table-set magic/header and includes serialized accept/default/base/next/check data for a minimal "notflex" DFA.

Control flow: `aa_setup_dfa_engine()` includes this file into `nulldfa_src[]`, unpacks it with `aa_dfa_unpack()` accepting 32-bit accept tables, assigns it to `nulldfa`, and attaches it to `nullpdb`. Null profiles and placeholder ancestors use `nullpdb` for file and policy rules, making this blob the default no-permission/learning placeholder engine.

State and persistence: static built-in data only; runtime state is the unpacked `aa_dfa` and `aa_policydb` references created during LSM init.

Dependencies and integration: tightly coupled to `match.c`'s serialized DFA format and `policy.c` null profile creation. Risks include silent corruption of a binary source file that is hard to review, mismatch with expected table flags, and boot failure if unpack verification rejects it. Test by boot/init of AppArmor, null profile allocation, DFA unpack validation, and comparing regenerated null DFA bytes from the policy compiler.
