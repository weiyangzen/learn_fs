## sources/distributed-fs/openafs/src/rxkad/der.h

### Purpose
`der.h` defines core Heimdal DER tag classes, tag types, universal tag constants, time helper structures, and DER helper prototypes used by rxkad Kerberos v5 code.

### Important APIs, Types, And Functions
It defines `Der_class`, `Der_type`, `MAKE_TAG`, universal tag constants, `ASN1_INDEFINITE`, `heim_der_time_t`, `heim_ber_time_t`, forward declaration `struct asn1_template`, includes `der-protos.h`, and declares internal helpers `_heim_fix_dce`, `_heim_der_set_sort`, and `_heim_time2generalizedtime`.

### Control Flow
No executable flow exists. Macros and enums encode DER tag bytes and classify primitive/constructed ASN.1 objects.

### State, Persistence, And Dependencies
The header has no mutable state and is guarded by `__DER_H__`. It requires ASN.1 type definitions such as `heim_octet_string` from included/generated Heimdal headers in the rxkad build.

### Integration Points
Ticket v5 DER code uses these definitions to parse and emit Kerberos structures. `der-protos.h` supplies the large generated function surface.

### Risks
Universal tag constants include unsupported aliases and a duplicate numeric value for `UT_UniversalString`/`UT_GraphicString`, matching ASN.1 numbering but easy to misuse. `ASN1_INDEFINITE` is a sentinel, not a normal length.

### Test Signals
Tests should validate tag construction, DER length/tag parsing, time conversion, SET sorting, DCE length fixups, and encode/decode compatibility with Kerberos ticket fixtures.
