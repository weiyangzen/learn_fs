# sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2_grpc.py

Purpose: generated gRPC companion for `ptypes/common.proto`. Because the proto defines only shared messages and no service, this file contains only the generated header/import of `grpc`.

Important APIs/types/functions: no stubs, servicers, registration functions, or experimental service helpers are exported.

Control flow: import-only module with no runtime RPC registration.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: depends on `grpc` solely because the gRPC plugin emitted a companion file. It may be imported by code expecting every `*_pb2.py` to have a matching `*_pb2_grpc.py`.

Risks: its emptiness is intentional; adding service-like code here would not match the proto. Removing it can break generated import conventions.

Test signals: import smoke test is enough; service discovery should not expect handlers from this file.
