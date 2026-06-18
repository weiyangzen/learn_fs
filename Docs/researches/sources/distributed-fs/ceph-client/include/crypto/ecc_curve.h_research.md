# sources/distributed-fs/ceph-client/include/crypto/ecc_curve.h

Purpose: elliptic curve metadata structures and lookup helpers.

Important APIs/types/functions: `struct ecc_point`, `struct ecc_curve`, `ecc_get_curve`, and `ecc_get_curve25519`.

Control flow: callers request curve parameters by ID or Curve25519 accessor and receive a const curve descriptor or NULL.

State and persistence: curve descriptors point to static field/order/parameter arrays and generator points.

Dependencies and integration points: used by ECDH/ECDSA/ECC implementations and keyed public-key code.

Risks: returned curve pointers are const shared data; callers must not mutate them. Curve IDs must match `ecdh.h` definitions. Header guard typo is benign but notable.

Test signals: curve lookup tests, ECDH/ECDSA vectors for supported curves, and NULL handling for unknown IDs.
