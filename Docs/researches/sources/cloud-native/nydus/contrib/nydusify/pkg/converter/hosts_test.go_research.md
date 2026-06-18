# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts_test.go

Purpose: tests host function insecure flag mapping and credential function creation.

Important APIs and flow: tests construct an `Opt` with source, target, chunk dictionary, and cache refs/insecure flags, call `hosts`, and verify each ref returns the expected boolean and non-nil Docker credential function. Unknown refs are expected to return secure false.

State and persistence: pure in-memory; Docker config credential function is not invoked.

Dependencies and integration: protects resolver configuration used by converter provider creation.

Risks and test signals: adequate for map behavior. It does not verify actual credential lookup from Docker config files.
