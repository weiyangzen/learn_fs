# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common.go

Purpose: provides shared pod, command, metadata, metrics, and secret-volume generation for JuiceFS mount pod builders.

Important APIs and types: `BaseBuilder` owns `*config.JfsSetting` and requested capacity. `genPodTemplate` builds a baseline pod from CSI pod attributes. `genCommonJuicePod` applies generated pod attributes, metadata, finalizer, service account, priority, restart policy, hostname, termination grace period, volumes, secret-sourced env vars, resources, lifecycle, probes, and metrics ports. Other helpers include `genHostname`, `genMountCommand`, `genInitCommand`, `getQuotaPath`, `getJobCommand`, `genMetricsPort`, `GenMetadata`, `_genMetadata`, and `_genJuiceVolumes`.

Control flow: common pod generation first refreshes pod attributes from config, adjusts encrypted init config compatibility, creates a container through a passed generator, overlays labels/annotations, mounts secret/config volumes, appends env vars, and chooses lifecycle/ports based on image support, webhook mode, host networking, and CE/EE mode. Command generation assembles CE or EE mount/format/job commands while handling subdir options, metrics defaults, RSA key options, readonly stripping for jobs, init config copies, and ACL config symlinks.

State and persistence behavior: builder methods are mostly pure transformations from `JfsSetting` to Kubernetes objects and shell strings, but `genCommonJuicePod` mutates `jfsSetting.InitConfig` when encrypted config is unsupported by the image. The resulting pods persist labels, annotations, finalizers, secret volumes, env vars, lifecycle hooks, and metrics ports in Kubernetes when created.

Dependencies and integration points: integrates global driver config, common labels/annotations/finalizers, security shell escaping, resource requirements from `PodAttr`, Kubernetes core APIs, and controller-runtime finalizer helpers. Downstream builders for pod/serverless/job modes reuse these helpers.

Risks and test signals: shell command construction is security-sensitive and relies on `security.EscapeBashStr` plus `util.QuoteForShell`. Metrics port parsing accepts up to six digits and does not validate port range. Map iteration over `Configs` yields nondeterministic volume order. Tests cover metadata generation and init command cases, not full pod templates, mount command generation, metrics parsing, or volume generation.
