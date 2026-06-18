## sources/cloud-native/buildkit/util/gogo/proto/enum.go

Purpose: compatibility helpers for enum JSON marshaling/unmarshaling formerly supplied by gogo/protobuf.

Important APIs: `MarshalJSONEnum(map[int32]string,value)` returns a JSON string of the symbolic enum name or decimal number if unknown. `UnmarshalJSONEnum(map[string]int32,data,enumName)` accepts quoted symbolic JSON or numeric JSON.

Control flow: unmarshal checks `data[0] == '"'` for string mode, decodes and map-lookups symbolic values, otherwise decodes an int32. Errors mention enum name and bad representation.

State/persistence: stateless. Dependencies: `encoding/json`, `strconv`, `pkg/errors`.

Integration points: used by generated or migrated proto enum code in BuildKit that still expects gogo-compatible helpers. Risks: assumes `data` is non-empty and can panic on empty input; unknown numeric values are accepted. Test signals: no local test in this subset.
