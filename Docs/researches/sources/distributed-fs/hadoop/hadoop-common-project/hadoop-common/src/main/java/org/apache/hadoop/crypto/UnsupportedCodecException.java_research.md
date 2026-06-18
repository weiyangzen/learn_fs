# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/UnsupportedCodecException.java

## Purpose
`UnsupportedCodecException` is a small unchecked exception used to signal that a requested Hadoop crypto codec is unavailable or unsupported.

## Important APIs and types
The class extends `RuntimeException` and provides four constructors: no-arg, message, message plus cause, and cause. It defines a stable `serialVersionUID`.

## Control flow
There is no custom control flow. Callers throw this exception directly when codec discovery or capability checks cannot satisfy a requested cipher implementation.

## State and persistence
It carries normal exception message/cause state only. It persists nothing.

## Dependencies and integration points
The class lives in `org.apache.hadoop.crypto` and is part of the crypto codec error model. It integrates with `CryptoCodec` selection and stream initialization paths that need to distinguish unsupported codecs from lower-level I/O errors.

## Risks
Because it is unchecked, callers may not be forced to handle codec unavailability. Messages should include enough configuration and cipher context at throw sites; this class itself does not enrich them.

## Test signals
Tests are minimal: serialization compatibility, constructor message/cause propagation, and integration tests asserting unsupported codec selection throws this type where expected.
