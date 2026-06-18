# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_cnt.go

Purpose: preserves the legacy `endpointCnt` datastore object for downgrade compatibility after endpoint reference counting became unused in v28.1. Important pieces are `endpointCnt`, `epCntKeyPrefix`, and its `datastore.KVObject` methods.

Control flow: methods expose key construction under `endpoint_count/<network-id>`, JSON value encoding/decoding, index/existence tracking, skip behavior based on `Network.persist`, object construction, and copy semantics. There is no active counter mutation logic here; `Count` is only serialized if old state is read or rewritten.

State/dependencies: state is a count plus datastore index/existence flags guarded by an embedded mutex and tied to a `Network` pointer. Dependencies include JSON and `datastore`. Integration point is backward/downgrade compatibility with previously persisted endpoint count records. Risks include `SetValue` unmarshalling into `&ec`, which changes a local pointer target rather than fields as a typical value receiver would, but this is legacy-only. Test signal is not local; behavior is mostly retained to avoid breaking old data.
