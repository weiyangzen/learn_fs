# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GaloisField.java

Purpose: general GF(2^p) arithmetic implementation, defaulting to GF(256) with primitive polynomial 285, used mainly by legacy RS code.

Important APIs/types/functions: singleton `getInstance()`/`getInstance(fieldSize, polynomial)`, arithmetic `add`, `multiply`, `divide`, `power`, polynomial `multiply`, `add`, `remainder`, `substitute`, bulk `solveVandermondeSystem` overloads, bulk `remainder`/`substitute`, and `gaussianElimination`.

Control flow: construction builds log, power, multiplication, and division tables. Singleton instances are cached under a synchronized map. Bulk methods apply table arithmetic over byte arrays or ByteBuffers at current offsets/positions, often mutating output/dividend buffers in place.

State and persistence: process-static singleton cache; per-instance lookup tables. No durable persistence.

Dependencies and integration: used by `RSUtil.GF`, legacy encoder/decoder, and RS primitive-power helpers.

Risks: many methods rely on Java `assert` for argument validation and mutate inputs. `gaussianElimination` pivot scan appears unusual (`matrix[i][j]`) and deserves regression coverage if used. Tests should cover arithmetic identities, Vandermonde solving, remainder/substitute byte and ByteBuffer paths, singleton cache behavior, and input mutation expectations.
