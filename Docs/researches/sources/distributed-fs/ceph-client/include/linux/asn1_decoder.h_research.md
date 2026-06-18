# sources/distributed-fs/ceph-client/include/linux/asn1_decoder.h

## Purpose
Declares the public ASN.1 BER decoder entry point.

## Important APIs, Types, And Functions
`asn1_ber_decoder(const struct asn1_decoder *decoder, void *context, const unsigned char *data, size_t datalen)` interprets a compiled ASN.1 decoder over an input buffer and caller-owned context.

## Control Flow, State, And Persistence
The decoder walks input bytes according to the provided bytecode and invokes action callbacks stored in `struct asn1_decoder`. State is transient for the decode call and caller-owned through `context`.

## Dependencies And Integration Points
Depends on `linux/asn1.h`, `linux/types.h`, and the forward-declared bytecode structure. Integrated by generated ASN.1 parser modules and security-sensitive parsers for keys, certificates, and signatures.

## Risks And Test Signals
Risks include accepting malformed BER/DER, out-of-bounds data reads, and callback context misuse. Tests should include fuzzed ASN.1 inputs, valid DER fixtures, truncated buffers, action callback failures, and grammar-specific parser validation.
