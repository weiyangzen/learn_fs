# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor_test.go

Purpose: baseline unit tests for cursor position and freeze behavior.

Important tests: empty cursor min is zero; `Advance` is monotonic and ignores backward/equal moves; zero/negative advances are ignored; min across keys returns the smallest timestamp; freeze blocks advances until unfreeze; freeze on unset seeds the position; snapshot/restore round-trips values and does not restore frozen flags.

Control flow/state: tests directly mutate cursor state through public methods and inspect positions via `Get`/`MinTsNs`.

Dependencies/integration: uses lifecycle action keys and action kinds; supports reader resume and dispatcher freeze logic.

Risks/gaps: concurrency behavior is protected by locks but not stress-tested here; composition tests cover deep copy/restore replacement, and race coverage would require running with `-race`.

Test signals: good branch coverage for the core cursor API.
