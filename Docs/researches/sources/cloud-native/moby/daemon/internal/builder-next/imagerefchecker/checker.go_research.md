# sources/cloud-native/moby/daemon/internal/builder-next/imagerefchecker/checker.go

## Purpose
Provides a BuildKit external reference checker that prevents cache garbage collection from deleting refs still used by Moby images.

## APIs, Control Flow, and Integration
`LayerGetter` abstracts lookup of a layer by snapshot/cache key. `Opt` wires `LayerGetter` and `image.Store`. `New` returns a `cache.ExternalRefCheckerFunc`. The checker lazily initializes once by walking all images and inserting each image rootfs diffID chain into an `lchain` trie. `Exists` caches answers by key, resolves the layer, reconstructs its parent diffID chain via `diffIDs`, and checks if that chain exists in the trie.

## State, Dependencies, and Risks
State is in-memory and per checker: `sync.Once`, trie, and key result cache. It reads the current image map only once, so newly created images after initialization are not reflected. Risks include recursion depth on long layer chains and false negatives if `LayerGetter` cannot resolve a key. Tests are indirect through cache GC behavior.
