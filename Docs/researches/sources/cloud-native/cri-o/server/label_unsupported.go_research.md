# sources/cloud-native/cri-o/server/label_unsupported.go

Purpose: non-Linux implementation of `securityLabel` where SELinux relabeling is unsupported or irrelevant.

Important APIs and functions: `securityLabel` accepts the same signature as the Linux implementation and returns nil.

Control flow: no validation, label lookup, or filesystem mutation occurs.

State and persistence: none.

Dependencies and integration: provides build-tag compatibility for server code that calls `securityLabel` on all platforms.

Risks: callers expecting enforcement should be aware that non-Linux platforms silently skip label application.

Test signals: no direct test; compile-time platform coverage is the main signal.
