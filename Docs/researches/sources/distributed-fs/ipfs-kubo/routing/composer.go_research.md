# sources/distributed-fs/ipfs-kubo/routing/composer.go

Purpose: implements a `routing.Routing` facade that dispatches each routing method to a method-specific underlying router.

Important APIs and control flow: `Composer` has router fields for get/put IPNS, peer lookup, provider lookup, and provide. Methods delegate directly and log debug details. `ProvideMany` only calls the underlying provide router when it implements `ProvideManyRouter`; otherwise it returns nil. `Ready` delegates when the provide router implements `ReadyAbleRouter`, else returns true. `Bootstrap` calls all five routers and joins errors.

State and persistence: no persistence; holds router references and delegates network/datastore state to them.

Dependencies and integration: produced by `routing.Parse`; integrates with libp2p routing interfaces and routing helper optional interfaces.

Risks and test signals: nil router fields will panic if a method is called without config assignment. Bootstrap may call the same router multiple times when methods share routers. Parser tests verify shared router instances for multiple methods.
