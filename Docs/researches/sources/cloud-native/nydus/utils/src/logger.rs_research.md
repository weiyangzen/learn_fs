# sources/cloud-native/nydus/utils/src/logger.rs

Purpose: bounded in-memory error/event holder that exports recent critical messages as JSON.

Important APIs/types/functions: `ErrorHolderError::{TooLarge,Serde}`, `Result<T>`, and `ErrorHolder`. `ErrorHolder` tracks `max_errors`, `total_errors`, `max_size`, `total_size`, and a `Mutex<VecDeque<String>>`. `new(max_errors, max_size)` constructs it. `push(&mut self, error)` timestamps an error with HTTP-date format and appends it while evicting old entries to satisfy count/size limits. `export(&self)` serializes the holder to JSON.

Control flow: `push` formats the incoming error with current time, then loops evicting from the front while adding the new message would exceed byte or count limits. If the new message is too large even after evicting all entries, it returns `TooLarge`. `export` locks the queue and serializes `self`; serde sees the mutex field through its `Serialize` support.

State and persistence: in-memory circular buffer only. Exported JSON can be persisted or exposed by diagnostics.

Dependencies and integration points: depends on `httpdate`, `serde`, `serde_json`, `Mutex`, and `VecDeque`. Useful for diagnostics endpoints or status reports where logs must be bounded.

Risks: `push` requires `&mut self` despite also using a mutex, limiting shared concurrent use unless wrapped externally. Size accounting uses `String::len` bytes and includes timestamp prefix. If `max_errors` or `max_size` is zero, most pushes will return `TooLarge`. Serialization while holding the lock could block pushers if external synchronization is added.

Test signals: overflow test pushes repeated errors to verify max count/size are respected and that an oversized message returns `TooLarge`.
