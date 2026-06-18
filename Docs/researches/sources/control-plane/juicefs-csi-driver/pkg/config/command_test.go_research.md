# sources/control-plane/juicefs-csi-driver/pkg/config/command_test.go

Purpose: tests `GetJfsVolUUID`, the subprocess-backed UUID discovery helper.

Important tests: the normal case monkey-patches `exec.Cmd.CombinedOutput` to return representative `juicefs config` output and asserts UUID extraction. The error case returns an exec error and expects a non-nil error. The EE case sets `IsCe=false` and verifies the setting name is returned without parsing CLI output.

Control flow/state: uses GoConvey and gomonkey; no real subprocess executes and no filesystem or Kubernetes state is touched.

Dependencies/integration: protects the UUID path used by `ParseSettingWithNode` when CE settings lack a UUID.

Risks/gaps: does not cover timeout behavior, database-not-formatted handling, malformed output without UUID, env propagation, `GenAuthCmd`, `GenFormatCmd`, escaping, or secret stripping.

Test signal: narrow but useful for CE/EE UUID branch behavior.
