## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeRestApiJsonifier.hh

Purpose: defines the tape-specific JSON serializer interface over the common EOS `Jsonifier`.

Important APIs/types/functions: template `TapeRestApiJsonifier<Obj>` inherits `common::Jsonifier<Obj>` and requires `void jsonify(const Obj*, std::stringstream&)`.

Control flow: concrete jsonifiers implement this interface and are attached to `Jsonifiable` models.

State and persistence: stateless interface.

Dependencies and integration points: used by tape JSON serializers and response models returned by `RestApiResponse`.

Risks and test signals: the interface does not enforce escaping or content type; tests should validate concrete serializers through HTTP response bodies.
