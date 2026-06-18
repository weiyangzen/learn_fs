# sources/cloud-native/containerd/internal/lazyregexp/lazyregexp.go

## Purpose
Delays regexp compilation for package-level regex variables until first use, while compiling immediately during tests to catch invalid patterns early.

## Important APIs, Types, And Functions
`Regexp` stores the pattern string, `sync.Once`, and compiled `*regexp.Regexp`. `New` constructs it. Methods proxy selected regexp operations: `FindStringIndex`, `FindStringSubmatch`, `MatchString`, `ReplaceAll`, and `String`.

## Control Flow
First method call invokes `re.once.Do(re.build)`, compiles with `regexp.MustCompile`, stores the regexp, and clears the source string. In test binaries, `New` compiles immediately.

## State And Persistence
In-memory lazy compiled regexp state. Once compiled, the original pattern string is discarded but `String()` can recover it from the regexp.

## Dependencies And Integration Points
Uses `regexp`, `sync`, `os.Args`, and string suffix checks. Copied from Go's module internals with added methods.

## Risks
Invalid patterns panic at first use in production but at construction in tests. Only a subset of regexp methods is exposed.

## Test Signals
`lazyregexp_test.go` verifies immediate panic for invalid regex under tests and successful matching for a valid pattern.
