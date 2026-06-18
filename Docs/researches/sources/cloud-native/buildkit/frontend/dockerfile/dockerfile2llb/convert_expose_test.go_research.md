# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose_test.go

Purpose: unit-tests EXPOSE port parsing.

Important test cases: empty spec errors, full IP/host/container ranges, bracketed and unbracketed IPv6 forms, tcp/udp/sctp protocols, host mapping forms, invalid hostname-as-IP, and multi-port range expansion.

Control flow and state: tests use package-level `ps := newPortSpecs()` and call parser methods directly; no LLB or image state is solved.

Dependencies and integration: validates helper behavior used by `dispatchExpose`.

Risks and test signals: strong parser coverage; lint warning behavior and image config mutation are not directly asserted here.
