# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_test.go

Purpose: Fuzzes `vniMatchBPF` over representative and arbitrary VNI inputs to ensure it does not panic.

Important APIs and functions: `FuzzVNIMatchBPFDoesNotPanic` seeds boundary-ish uint32 values and calls `vniMatchBPF` for fuzzed inputs.

Control flow: fuzz target ignores output and checks panic-free assembly.

State and persistence: stateless.

Dependencies and integration points: covers the non-Linux-safe part of BPF program construction.

Risks: does not verify semantic matching; that is handled by Linux raw socket test.

Test signals: catches future instruction-construction changes that make BPF assembly invalid for some input.
