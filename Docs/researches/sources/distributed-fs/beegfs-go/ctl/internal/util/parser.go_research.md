# sources/distributed-fs/beegfs-go/ctl/internal/util/parser.go

Purpose: implements parsing and formatting helpers for byte sizes, numeric ranges, and "unlimited" int64 display.

Important APIs/types/functions: `ParseIntFromStr`; `ParseUint64RangeFromStr`; `I64FormatPrefixWithUnlimited`; `UnlimitedText`; SI/IEC multiplier map.

Control flow: byte parsing matches `<number><optional unit>`, validates units, uses integer multiplication for whole numbers to preserve precision, rejects decimal raw bytes, and checks overflow for integer and float paths. Range parsing accepts `min-max` or a single value and enforces configured bounds. Unlimited formatting maps `math.MaxInt64` to infinity text, otherwise delegates to unitconv.

State and persistence: stateless.

Dependencies and integration points: used by flag helpers and other command packages needing size/range parsing. Depends on regex, strconv, math, strings, and unitconv.

Risks: regex allows multiple dots initially and relies on later parsing errors. Float conversion for decimal prefixed values can lose precision for very large values, as documented. Unit spelling is intentionally strict around uppercase `B`, which may reject user expectations.

Test signals: `parser_test.go` covers valid SI/IEC inputs, decimals with prefixes, invalid units, max uint64 boundaries, overflow, raw-byte decimal rejection, and range parsing with bounds/order errors.
