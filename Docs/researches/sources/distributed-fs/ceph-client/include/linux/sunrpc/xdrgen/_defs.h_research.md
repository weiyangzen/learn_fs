# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_defs.h

Purpose: defines base C representations and fixed XDR word-size constants for generated SUNRPC XDR code.

Important APIs and types: `TRUE` and `FALSE` map to C booleans. `typedef struct { u32 len; unsigned char *data; } string;` represents XDR strings. `typedef struct { u32 len; u8 *data; } opaque;` represents XDR opaque data. Size macros define word counts for void, bool, int, unsigned int, long, unsigned long, hyper, and unsigned hyper.

Control flow: generated headers use these definitions to declare protocol structs and compute static maximum encoded sizes.

State and persistence: no state; decoded pointers point into separately managed XDR buffers.

Dependencies and integration points: included by generated XDR protocol headers and assumes kernel integer and bool types are available from the including context.

Risks and test signals: risks include confusing byte length with XDR word counts, pointer lifetime misuse, and generated-code ABI drift. Test by regenerating XDR headers, compiling protocol users, and validating max-size macros against encoded test vectors.
