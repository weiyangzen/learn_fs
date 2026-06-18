# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestMarshalling.java

Purpose: tests JSON marshalling and validation of registry `ServiceRecord` instances.

Important APIs and functions: class-level `ServiceRecordMarshal`; `testRoundTrip()` validates serialization/deserialization of custom attributes; negative tests cover empty bytes, truncated JSON, invalid JSON, wrong type, long nonmatching type, missing service record type, and wrong validation type. Additional tests verify unknown field round-trip and copy constructor propagation.

Control flow: positive paths create a record, validate it with `RegistryTypeUtils`, serialize to bytes, deserialize, and compare attributes and endpoint counts. Negative paths assert specific registry exceptions (`NoRecordException` or `InvalidRecordException`).

State and persistence: all state is in-memory byte arrays and `ServiceRecord` objects. No external registry dependency.

Dependencies and integration: depends on `RegistryUtils.ServiceRecordMarshal`, `ServiceRecord`, persistence policies, helper assertions, and registry record validation code.

Risks and test signals: good signal for malformed input handling and custom attribute preservation. It does not test very large records, Unicode payloads, or compatibility with external JSON libraries beyond the local marshal implementation.
