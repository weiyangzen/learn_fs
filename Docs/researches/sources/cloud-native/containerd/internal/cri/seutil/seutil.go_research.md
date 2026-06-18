# Research: sources/cloud-native/containerd/internal/cri/seutil/seutil.go

This SELinux utility file provides `ChangeToKVM`, a helper for converting an existing process label to use the SELinux type from KVM container labels. If the input label is empty or SELinux is disabled, it returns an empty string and nil error. Otherwise it asks SELinux for KVM container labels, immediately releases the generated process label reservation, parses both the current label and KVM process label into SELinux contexts, replaces the current context's `type` field with the KVM type, and returns the resulting label string.

The control flow is intentionally small but has process-global SELinux integration. It depends on `opencontainers/selinux/go-selinux` for enablement checks, generated KVM labels, label release, context parsing, and context rendering. There is no local persistence, but SELinux label reservation/release affects global label allocation state.

Risks include invalid input labels returning parse errors, errors from parsing generated KVM labels, releasing a generated label while keeping only its type, and returning an empty label rather than the original label when SELinux is disabled. The helper is likely used by VM/Kata/KVM runtime paths that need KVM-compatible process types while preserving MLS/MCS level and other context fields. No direct tests are listed for this file.
